import xbmc
import xbmcgui

from radioparadise import STREAM_INFO, NowPlaying


class Player(xbmc.Player):
    """Adds xbmc.Player callbacks and integrates with the RP API."""

    def __init__(self):
        """Constructor"""
        super().__init__()
        self.last_key = None
        self.now_playing = None

    def get_song_key(self):
        """Return (artist, title) for the current song, or None."""
        result = None
        if self.isPlayingAudio():
            try:
                info = self.getMusicInfoTag()
                result = (info.getArtist(), info.getTitle())
            except Exception:
                pass
        return result

    def update(self):
        """Update RP API and music player information."""
        now_playing = self.now_playing
        if now_playing:
            now_playing.update()

        song_key = self.get_song_key()
        if song_key == self.last_key:
            return

        xbmc.log(f'Song: {song_key}', xbmc.LOGINFO)
        if song_key and now_playing:
            song_data = now_playing.get_song_data(song_key)
            if song_data and 'cover' in song_data:
                cover = song_data['cover']
                xbmc.log(f'Cover: {cover}', xbmc.LOGINFO)
                info = build_music_info(song_key, song_data)
                item = xbmcgui.ListItem()
                item.setPath(self.getPlayingFile())
                item.setArt({'thumb': cover})
                item.setInfo('music', info)
                self.updateInfoTag(item)
                self.last_key = song_key
        else:
            self.last_key = song_key

    def onAVStarted(self):
        if self.isPlayingAudio() and self.getPlayingFile() in STREAM_INFO:
            xbmc.executebuiltin('Action(FullScreen)')
        else:
            self.now_playing = None

    def onPlayBackEnded(self):
        self.now_playing = None

    def onPlayBackError(self):
        self.now_playing = None

    def onPlayBackStarted(self):
        info = STREAM_INFO.get(self.getPlayingFile())
        if info is not None:
            self.now_playing = NowPlaying(info['channel'])
        else:
            self.now_playing = None

    def onPlayBackStopped(self):
        self.now_playing = None


def build_music_info(song_key, song_data):
    """Return a dict for Player.updateInfoTag()."""
    result = {
        'artist': song_key[0],
        'title': song_key[1],
        'genre': '',
    }
    if 'album' in song_data:
        result['album'] = song_data['album']
    if 'rating' in song_data:
        result['rating'] = float(song_data['rating'])
        result['userrating'] = int(round(float(song_data['rating'])))
    if 'year' in song_data:
        result['year'] = int(song_data['year'])
    return result


if __name__ == '__main__':
    player = Player()
    monitor = xbmc.Monitor()
    while not monitor.abortRequested():
        if monitor.waitForAbort(0.1):
            break
        try:
            player.update()
        except Exception as e:
            xbmc.log(f'rp_service: {e}', xbmc.LOGERROR)
