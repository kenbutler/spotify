Your Spotify credentials file and exported iTunes library file (e.g. Library.xml) should be placed here.

The Spotify credentials file should follow this format:
```
<username>
<client id>
<client secret>
[comma-separated list of playlists names to ignore]
```

This transfer utility does _NOT_ assume that any playlists should be ignored. 
There are some playlists that probably should be ignored though. For example:
```
All,Music,Movies,TV Shows,Podcasts,Audiobooks,Library,Purchased,Recently Added,Recently Played,Top 25 Most Played
```