[![PyPI release](https://img.shields.io/pypi/v/defederate)](https://pypi.org/projects/defederate)
[![Supported Python versions](https://img.shields.io/pypi/pyversions/defederate)](https://pypi.org/projects/defederate)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![BSD License](https://img.shields.io/pypi/l/defederate)](https://github.com/Anthchirp/mastodon-defederate/blob/main/LICENSE)

# Tools for Mastodon Instance Blocklist Management

If you are running a small Mastodon instance then you do not have the benefit
of moderation teams that larger instances have. This means that you may see
toots from instances that you are not interested in.

Particularly when you use relays to discover interesting content there is a
high probability that you will quickly discover eg. openly racist instances
that nobody in their right mind needs or wants.
With a personal mastodon instance it will be your job to either block
individual users from those instances, or manually defederate (that is: block)
the server for everyone on your instance.

So if you trust some larger instance to do a good job at maintaining their
instance block list then this tool allows you to piggyback on their work and
use their blocklists on your instance.

## Installation

You will need Python 3.6+ with `pip`.
Then run `pip install defederate`.

## Parse a public 3rd-party blocklist

```bash
$ defederate show social.example.com
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
$ defederate show https://github.com/chaossocial/about/raw/master/blocked_instances.md
```

## Notes

* [Concerns](https://mast.uxp.de/web/@ondra@unextro.net/109336212305901991)
* [Similar/related project](https://gitlab.comwork.io/oss/mastodon-term-services)
* [Similar/related project](https://github.com/hachyderm/hack)
* [Similar/related project](https://mastodon-tools.dingelstad.works/)
* [related Mastodon PR](https://github.com/mastodon/mastodon/pull/15664)
