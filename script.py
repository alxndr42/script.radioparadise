import xbmc
import xbmcaddon
import xbmcgui

from radioparadise import STREAMS


class Window(xbmcgui.WindowXML):
    def onInit(self):
        xbmc.executebuiltin('Container.SetViewMode(50)')
        listitems = []
        for s in STREAMS:
            item = xbmcgui.ListItem(s['title'])
            item.setProperty('url_aac', s['url_aac'])
            item.setProperty('url_flac', s['url_flac'])
            listitems.append(item)
        self.clearList()
        self.addItems(listitems)
        xbmc.sleep(100)
        self.setFocusId(self.getCurrentContainerId())

    def onClick(self, controlId):
        if controlId == 50:
            audio_format = addon.getSetting('audio_format')
            item = self.getListItem(self.getCurrentListPosition())
            if audio_format == 'flac':
                url = item.getProperty('url_flac')
            else:
                url = item.getProperty('url_aac')
            play_url(url)
            self.close()


def play_url(url):
    """Play the URL, unless it's already playing."""
    player = xbmc.Player()
    if not player.isPlayingAudio() or player.getPlayingFile() != url:
        player.stop()
        player.play(url)


if __name__ == '__main__':
    addon = xbmcaddon.Addon()
    addon_path = addon.getAddonInfo('path')
    window = Window('radioparadise.xml', addon_path)
    window.doModal()
    del window
