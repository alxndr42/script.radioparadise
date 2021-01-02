import xbmc
import xbmcgui

from radioparadise import STREAM_INFO, NowPlaying


class Player(xbmc.Player):
    """Adds xbmc.Player callbacks and integrates with the RP API."""

    def __init__(self):
        """Constructor"""
        super().__init__()
        self.last_key = None
        self.now_playing = NowPlaying()

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

    def reset(self):
        """Reset internal state when not playing RP."""
        self.last_key = None
        self.now_playing.set_channel(None)

    def update(self):
        """Update RP API and music player information."""
        self.now_playing.update()

        song_key = self.get_song_key()
        if song_key == self.last_key:
            return
        if song_key is None:
            self.last_key = None
            return

        xbmc.log(f'Song: {song_key}', xbmc.LOGINFO)
        song_data = self.now_playing.get_song_data(song_key)
        if song_data is None:
            return

        cover = song_data.get('cover', '')
        info = build_music_info(song_key, song_data)
        item = xbmcgui.ListItem()
        item.setPath(self.getPlayingFile())
        item.setArt({'thumb': cover})
        item.setInfo('music', info)
        self.updateInfoTag(item)
        self.last_key = song_key

    def onAVStarted(self):
        if self.isPlaying() and self.getPlayingFile() in STREAM_INFO:
            url = self.getPlayingFile()
            info = STREAM_INFO[url]
            # Kodi switches to fullscreen for FLAC, but not AAC
            if url == info['url_aac']:
                xbmc.executebuiltin('Action(FullScreen)')
        else:
            self.reset()

    def onPlayBackEnded(self):
        self.reset()

    def onPlayBackError(self):
        self.reset()

    def onPlayBackStarted(self):
        if self.isPlaying() and self.getPlayingFile() in STREAM_INFO:
            url = self.getPlayingFile()
            info = STREAM_INFO[url]
            self.now_playing.set_channel(info['channel'])
        else:
            self.reset()

    def onPlayBackStopped(self):
        self.reset()


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
