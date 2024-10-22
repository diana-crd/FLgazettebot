FLgazettebot is an automated Python utility to publish updates on the [Fallen London](https://www.fallenlondon.com/) browser game's weekly *World Qualities* live events. It uses the MediaWiki REST API to fetch gameplay information from the game’s fan wiki, then formats it into readable, helpful blog posts. At the moment it only supports posting to Tumblr but I'm planning to also add Telegram channel functionality in the future. The bot's front-facing Tumblr blog can be found at https://theunexpurgatedlondongazette.tumblr.com/
##### Acknowledgements
- Fallen London is © and ™ Failbetter Games Limited; this is a fan project and is unaffiliated with Failbetter Games.
- Tumblr API interfacing is managed through the [pytumblr2](https://github.com/nostalgebraist/pytumblr2/) fork of the official Tumblr API Python client.
- Gameplay information and World Quality status is taken from the [Unofficial Fallen London Wiki](https://fallenlondon.wiki).

The content of this repository is available under [Creative Commons Attribution-ShareAlike](https://creativecommons.org/licenses/by-sa/3.0/).