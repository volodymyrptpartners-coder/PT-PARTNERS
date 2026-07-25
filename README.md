### Instalation
```sh
# Requisites
# python 3.8.10
# Create environment
python3 -m venv python_environment
source python_environment/bin/activate
python3 -m pip install poetry


poetry config keyring.enabled false
poetry install

alias tree='tree -I "python_environment|__pycache__"'



# Regeneration autocomplection
sitegen --show-completion >> python_environment/bin/activate
poetry shell
```

### Documentation
```sh
sitegen --help
```


### Technologies
```
CookieBot - consent cookie table !!!!!
or block cookie_consent_v2 
https://digitalmicroenterprise.com/cookie-consent-with-google-tag-manager


Cloudflare - bot protection !!!!
https://ryanhopkins.dev/articles/automatically-block-bad-bot-traffic-for-free-with-cloudflare



# Create arhive
tar cvf site.tar   --exclude="*/__pycache__"   --exclude="pt-clone/python_environment/*" --exclude="pt-clone/.mypy_cache" --exclude="*/.pytest_cache" --exclude="*/.git" --exclude="*/.ruff_cache"  pt-clone/

```
