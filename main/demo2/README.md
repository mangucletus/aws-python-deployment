# Demo 2 — Flask Behind An ALB With An Auto Scaling Group

This builds on [demo1](../demo1/README.md) by putting an **Application Load Balancer** in front of multiple Flask instances managed by an **Auto Scaling Group (ASG)** that scales on CPU.

## Architecture

```
              ┌────────────────────┐
   Internet ──▶  Application LB    │   (HTTP :80)
              │  flask-demo-alb    │
              └─────────┬──────────┘
                        │  forwards to TG
              ┌─────────▼──────────┐
              │   Target Group     │   health check: GET /health → 200
              │  HTTP :80          │
              └─────────┬──────────┘
                        │
            ┌───────────┼───────────┐
            │           │           │
        ┌───▼──┐    ┌───▼──┐    ┌───▼──┐
        │ EC2  │    │ EC2  │    │ EC2  │  Auto Scaling Group
        │      │    │      │    │      │  flask-demo-asg
        └──────┘    └──────┘    └──────┘  scales on CPU @ target
```

## Components You Need In AWS

| Resource | Purpose |
| --- | --- |
| **Launch Template** (`flask-demo-lt`) | Defines AMI, instance type, key pair, user-data (use the script from [../demo1/README.md](../demo1/README.md)), security group for instances |
| **Auto Scaling Group** (`flask-demo-asg`) | Manages the fleet; min/desired/max capacity; references the launch template |
| **Target Group** (HTTP :80, `/health`) | ALB routes traffic here; ASG registers instances here |
| **Application Load Balancer** (`flask-demo-alb`) | Public entry point; HTTP :80 listener forwards to the target group |
| **Security Groups** | ALB SG: allow `:80` from `0.0.0.0/0`. Instance SG: allow `:80` **from the ALB SG only**. |
| **Scaling Policy** | Target-tracking on `ASGAverageCPUUtilization` (e.g., 50%) |

## Security Group Wiring (commonly fumbled)

The instance SG **must allow port 80 inbound from the ALB's SG ID** — not from `0.0.0.0/0`. If you only allow it from `0.0.0.0/0` your app is exposed directly; if you allow nothing, the ALB can't reach it and you'll see 502s + failing health checks.

For SSH access to instances behind this setup, prefer **Systems Manager Session Manager** (no inbound rule needed) — the instance role just needs the `AmazonSSMManagedInstanceCore` policy.

## Common Failures While Building This

| Symptom | Cause | Fix |
| --- | --- | --- |
| 502 Bad Gateway from ALB | App not running on instances, or wrong port | SSH/SSM in, run `sudo systemctl status flaskapp`, fix the user-data per [demo1](../demo1/README.md) |
| Targets stuck `unhealthy` | Health check path mismatch, or instance SG blocks ALB SG | Target group health check path = `/health`, success codes = `200`. SG inbound :80 must allow the ALB SG |
| Targets stuck `unhealthy` only in some AZs | ALB enabled subnets don't overlap with ASG AZs | Console → ALB → Network mapping → enable the AZs your ASG uses |
| EC2 Instance Connect "Failed to connect" | Instance SG only allows the ALB | Use Session Manager instead (no SG change needed) |

---

# Stress Testing The Application (verifying Auto Scaling)

End-to-end procedure to prove that scale-out fires when CPU crosses your target.

## Prerequisites

- ASG (`flask-demo-asg`) backed by a launch template (`flask-demo-lt`).
- A **target-tracking scaling policy** on `ASGAverageCPUUtilization` (e.g., target = 50%).
- ASG `MaxSize > DesiredCapacity` (otherwise scale-out has no headroom).
- A way to reach an instance shell:
  - **Session Manager** (works with zero inbound SG rules) — requires IAM role `AmazonSSMManagedInstanceCore` on the instance.
  - Or SSH (port 22 inbound from your IP).

## Step 1 — Confirm the policy and alarms exist

```bash
aws autoscaling describe-policies \
  --auto-scaling-group-name flask-demo-asg --region eu-west-1

aws cloudwatch describe-alarms --region eu-west-1 \
  --query "MetricAlarms[?Dimensions[?Value=='flask-demo-asg']].[AlarmName,StateValue,Threshold]" \
  --output table
```

You should see `AlarmHigh` (above target) and `AlarmLow` (below target × 0.7).

## Step 2 — Generate load on an instance

Pick any in-service ASG instance, SSH/SSM in, then:

```bash
# Install stress-ng (Ubuntu)
sudo apt-get update -y
sudo apt-get install -y stress-ng

# Or on Amazon Linux 2023
# sudo dnf install -y stress-ng

# How many vCPUs?
nproc

# Run in background for 30 minutes — survives the SSH session ending
nohup stress-ng --cpu $(nproc) --cpu-load 95 --timeout 1800s --oom-avoid \
  > /tmp/stress.log 2>&1 &
echo "PID $!"

# Verify it's running and CPU is pinned
pgrep -af stress-ng
top -bn1 | head -5
```

## Step 3 — Watch the metric, alarm, and ASG (from your laptop)

```bash
# Live CPU on the ASG
watch -n 30 'aws cloudwatch get-metric-statistics --region eu-west-1 \
  --namespace AWS/EC2 --metric-name CPUUtilization \
  --dimensions Name=AutoScalingGroupName,Value=flask-demo-asg \
  --start-time $(date -u -d "10 minutes ago" +%FT%TZ) \
  --end-time   $(date -u +%FT%TZ) \
  --period 60 --statistics Average \
  --query "sort_by(Datapoints, &Timestamp)" --output table'

# Alarm state — flips OK → ALARM after sustained breach
watch -n 15 "aws cloudwatch describe-alarms --region eu-west-1 \
  --query \"MetricAlarms[?Dimensions[?Value=='flask-demo-asg']].[AlarmName,StateValue,Threshold]\" \
  --output table"

# Recent scale-out / scale-in events
watch -n 15 'aws autoscaling describe-scaling-activities --region eu-west-1 \
  --auto-scaling-group-name flask-demo-asg --max-items 5 \
  --query "Activities[].[StartTime,StatusCode,Cause]" --output table'

# Live instance list
watch -n 15 'aws autoscaling describe-auto-scaling-groups --region eu-west-1 \
  --auto-scaling-group-names flask-demo-asg \
  --query "AutoScalingGroups[0].Instances[].[InstanceId,LifecycleState,HealthStatus]" \
  --output table'
```

## Expected Timeline

| T+ | Event |
| --- | --- |
| 0 min | `stress-ng` starts → CPU pinned to ~95% |
| 1–2 min | First high CPU data points reach CloudWatch (1-min if detailed monitoring, else 5-min) |
| ~3 min | `AlarmHigh` transitions `OK → ALARM` (default = 3 consecutive periods over threshold) |
| 3–4 min | ASG `Activity` tab: `Launching a new EC2 instance` |
| 6–10 min | New instance: `Pending → Pending:Wait → InService`, registered in target group |

## Common Gotchas

| Symptom | Cause | Fix |
| --- | --- | --- |
| `Monitoring` tab shows "No data available" | Basic monitoring (5-min granularity) — UI hasn't ingested yet | Enable detailed monitoring: `aws ec2 monitor-instances --instance-ids <id>` |
| CPU stuck at ~20% even with `stress-ng` running 100% | `t3.micro` / `t3.small` ran out of CPU credits → throttled to baseline | Switch to non-burstable type (`m6i.large`, `c6i.large`) **or** enable T3 Unlimited (`modify-instance-credit-specification ... CpuCredits=unlimited`) |
| `Blocked: This account cannot run burstable instances with Unlimited enabled` | Sandbox/test account restriction | Use a non-burstable instance type, or lower the alarm threshold to fit the throttled baseline (~15%) just to see scale-out fire |
| Alarm fires but no scale-out | `MaxSize == DesiredCapacity` | `aws autoscaling update-auto-scaling-group --auto-scaling-group-name flask-demo-asg --max-size 4` |
| Alarm never fires | Wrong dimensions on alarm, or policy not attached to ASG | Re-check `describe-policies` and `describe-alarms` |

## Scaling Back Down After The Test

Once you `pkill stress-ng`, target tracking will eventually scale in via `AlarmLow` — but this can take 15+ min by default. To clean up immediately:

```bash
# 1) On the stress instance — stop the load
pkill stress-ng

# 2) Wait ~2-3 min so AlarmHigh leaves the ALARM state. Confirm:
aws cloudwatch describe-alarms --region eu-west-1 \
  --query "MetricAlarms[?Dimensions[?Value=='flask-demo-asg']].[AlarmName,StateValue]" \
  --output table
# AlarmHigh should be OK before continuing

# 3) Force ASG back to its baseline
aws autoscaling update-auto-scaling-group \
  --auto-scaling-group-name flask-demo-asg \
  --min-size 1 --desired-capacity 1 \
  --region eu-west-1
```

If you skip step 2 and the high alarm is still firing, the policy will fight your manual `desired-capacity = 1` and immediately scale back up. If you really need to force it regardless, suspend the scaling process first:

```bash
aws autoscaling suspend-processes \
  --auto-scaling-group-name flask-demo-asg \
  --scaling-processes AlarmNotification \
  --region eu-west-1

aws autoscaling update-auto-scaling-group \
  --auto-scaling-group-name flask-demo-asg \
  --desired-capacity 1 --region eu-west-1

# Resume autoscaling when you want it back
aws autoscaling resume-processes \
  --auto-scaling-group-name flask-demo-asg \
  --scaling-processes AlarmNotification \
  --region eu-west-1
```
