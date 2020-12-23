# Purpose

This project was motivated by my wife wanting to access my curated iTunes playlists on her Spotify account. 
Of course, I am "old school" and refuse to subscribe to any streaming services.
As of February 2018, [Spotify decided to remove the iTunes import feature](https://community.spotify.com/t5/Desktop-Windows/iTunes-import-missing/td-p/4466633).
In other words, taking the _easy_ way out was no longer an option.

Alas, I am a software developer myself and refuse to be shutdown from this inconvenience.

# Requirements
Python 3.7+

See _requirements.txt_ for requried Python packages

# Caveats
Learned a few things in this little escapade.
- While iTunes allows you to create folders for playlists, these folders are actually playlists themselves.
No folders actually exist. I do a check to ensure no folders are added.
- Playlist names must be unique.
Though iTunes allows you to name playlists with duplicate names, they still track them behind the scenes with unique IDs.
When transferring playlists to Spotify, though, it's pretty important to make sure all your iTunes playlist names are unique.
You might otherwise end up with a merging of two different playlists with the same name.
- Spotify's REST API places limits on queries.
For example, you can only query the names of 50 playlists at a time, or add 100 tracks to a playlist at a time.
I've handled these sort of limits (at least the ones I've encountered so far) in the code.

# How to Use
To use this project, follow these steps:
1. **Clone down this repository.** Let's call the location of this repository _{ROOT}_
2. **Export iTunes library to {ROOT}/res/.** Typically this involves opening iTunes and selecting _File > Library > Export Library..._
Apple should default to the name of _Library.xml_, but other names are fine too.
Make sure you export this to the resources directory of the repository.
3. **Create a Spotify credentials file in the resources (res/) directory.**
The recommended name for the Spotify credentials file is _spotify_credentials.txt_.
The Spotify credentials file should follow this format:
```
<username>
<client id>
<client secret>
[comma-separated list of playlists names to ignore]
```
To get your client ID and secret, checkout the [Authorization Guide](https://developer.spotify.com/documentation/general/guides/authorization-guide/).
This transfer utility does _NOT_ assume that any playlists should be ignored. 
There are some playlists that probably should be ignored though. For example:
```
All,Music,Movies,TV Shows,Podcasts,Audiobooks,Library,Purchased,Recently Added,Recently Played,Top 25 Most Played
```
4. **Run _transfer.py_.**
**_CAUTION_**: This should clear all playlists on your Spotify account and make it completely automated through this script.

# Help
If you run into HTTP issues, I recommend looking at
[Spotify's developer documentation](https://developer.spotify.com/documentation/web-api/) 
for a match/explanation of the error code they provide.