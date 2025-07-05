# Cron validator for Python

Do you need a cron validator?

I got sick of importing cron libraries that were deprecated or didn't function as expected.

I just wanted a validator and that's it.

## What it does

It does one thing. It validates a crontab through one function.

```python
import validator

validator.is_cron_valid("[your-cron-expression]")

```
