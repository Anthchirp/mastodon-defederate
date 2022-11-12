# Tools for Mastodon Instance Blocklist Management


## Installation

You will need Python 3.6+ with `pip`.
Then run `pip install defederate`.

## Parse a public blocklist

You will need to specify the Mastodon server version (3 or 4):

```bash
$ defederate show --mastodon-version 4 social.example.com   
Current blocklist on social.example.com:
 SILENCE: badhost1.example.com
 SILENCE: badhost2.example.com
 (...)
 SUSPEND: badhost1.example.net
 SUSPEND: badhost2.example.net
 (...)
```

The server you are requesting the blocklist from must allow public access.

This can also parse blocklists in Markdown format, for example the [blocklist](https://github.com/chaossocial/about/raw/master/blocked_instances.md) used by [chaos.social](https://chaos.social):
```bash
$ defederate show --mastodon-version markdown https://github.com/chaossocial/about/raw/master/blocked_instances.md
```
