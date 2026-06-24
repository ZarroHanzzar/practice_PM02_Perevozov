# Runbook Аварийного Восстановления (DR) — Магнолия

**Версия:** 1.0
**Для дежурного инженера:** Действовать строго по шагам.
**Контакты:** @on-call (Slack), +7-XXX-XXX-XX-XX

---

## Сценарий 1: Восстановление базы лояльности (PostgreSQL + Redis)

**Цель:** RTO < 1 час, RPO < 5 мин

---

### Шаг 1. Подготовка инфраструктуры (0-5 мин)

```bash
# Переключить DNS на резервный регион (если основной упал)
aws route53 change-resource-record-sets \
    --hosted-zone-id Z123456 \
    --change-batch file://failover.json

# Развернуть новую инфраструктуру через Terraform
cd /terraform/dr/
terraform apply -auto-approve -var="env=dr"

# Проверить, что EC2 и RDS запущены
aws ec2 describe-instances --region us-west-2 --filters "Name=tag:Role,Values=backend"