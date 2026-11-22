# Copyright (C) 2018-2026 by xcentaurix
# License: GNU General Public License v3.0


from enigma import BT_ALIGN_CENTER, RT_BLEND, RT_HALIGN_CENTER, RT_VALIGN_CENTER, eListbox, eSize
from Tools.Directories import SCOPE_PLUGINS, resolveFilename
from Tools.LoadPixmap import LoadPixmap
from Components.Addons.Pager import Pager
from Components.MultiContent import MultiContentEntryPixmapAlphaBlend, MultiContentEntryText
from Components.Sources.COCPageSource import COCPageSource

IMAGES = "SystemPlugins/ComponentsCockpit/skin/images/"


class COCPager(Pager):
    """The Pager with four changes.

    Page numbers from the plugin: connected to a COCPageSource it shows the pages the plugin sets there, connected to
    anything else it works like the Pager.

    A bubble that stays where it is: with more pages than maxPages the Pager shows "3 / 12" between two arrows. It places
    the group by the number of arrows (two on a middle page, one on the first and the last), so the bubble jumps when an
    arrow comes or goes. Here the bubble is centred and the arrows sit beside it.

    Arrows in every skin: the Pager takes its arrows from the icons of the active skin (shevronleft.png and
    shevronright.png), and a skin without them shows none. Here the images of ComponentsCockpit are the fallback; a
    picL or picR of the skin still wins.

    The pages of a text right: connected to a ScrollLabel it counts the last page where the text ends (the Pager shows
    the wrong page when the height of the text is a multiple of the height of the label)."""

    def __init__(self):
        Pager.__init__(self)
        for attribute, name in (("picShevronLeft", "shevronleft"), ("picShevronRight", "shevronright")):
            if not getattr(self, attribute):
                setattr(self, attribute, LoadPixmap(resolveFilename(SCOPE_PLUGINS, IMAGES + name + ".png")))

    def initPager(self):
        if isinstance(self.source, COCPageSource):
            # the Pager counts from 0 and takes the number of the last page
            self.selChange(max(self.source.currentPage - 1, 0), max(self.source.pageCount - 1, 0))
        elif self.source.__class__.__name__ == "ScrollLabel":
            self.selChange(*self.scrollLabelPages(self.source))
        else:
            Pager.initPager(self)

    @staticmethod
    def scrollLabelPages(label):
        """(current page, last page), counted from 0, of a ScrollLabel. The last page is where the text ends: the label stops
        there, in the middle of a page, so a position at the end is the last page whatever it is divided by."""
        page = label.pageHeight
        if page <= 0 or label.TotalTextHeight <= page:
            return 0, 0
        last = -(-label.TotalTextHeight // page) - 1
        return (last if label.curPos >= label.TotalTextHeight - page else label.curPos // page), last

    def buildEntry(self, currentPage, pageCount):
        bubble = (self.picDotPage and self.showIcons == "showAll" and self.orientation == eListbox.orHorizontal
                  and getattr(self, "current_page_style", getattr(self, "currentPageStyle", None)) == "bubbletext"
                  and 0 < getattr(self, "max_pages", getattr(self, "maxPages", 0)) < pageCount)
        if not bubble:
            return Pager.buildEntry(self, currentPage, pageCount)
        width = self.l.getItemSize().width()
        height = self.l.getItemSize().height()
        pixdWidth = self.picDotPage.size().width()
        pixdHeight = self.picDotPage.size().height()
        text = f"{currentPage + 1} / {pageCount + 1}"
        textWidth = self._calcTextWidth(text, font=self.font, size=eSize(self.getDesktopWith() // 3, 0))
        _padding = getattr(self, "bubbletextPadding", getattr(self, "bubbletext_padding", 4))
        bubbleWidth = textWidth + _padding * 2
        xBubble = (width - bubbleWidth) // 2
        res = [None]
        if currentPage > 0 and self.picShevronLeft:
            res.append(MultiContentEntryPixmapAlphaBlend(
                pos=(xBubble - self.spacing - pixdWidth, 0), size=(pixdWidth, pixdHeight), png=self.picShevronLeft,
                backcolor=None, backcolor_sel=None, flags=BT_ALIGN_CENTER))
        _bubble_bg = getattr(self, "bubbletextBkColor", getattr(self, "bubbletextBackgroundColor", getattr(self, "bubbletext_background_color", None)))
        _corner_radius = getattr(self, "bubbletextCornerRadius", getattr(self, "bubbletext_corner_radius", 0))
        try:
            res.append(MultiContentEntryText(
                pos=(xBubble, 0), size=(bubbleWidth, height), font=0, flags=RT_HALIGN_CENTER | RT_VALIGN_CENTER, text=" ",
                cornerRadius=_corner_radius, backcolor=_bubble_bg, backcolor_sel=_bubble_bg))
        except TypeError:
            res.append(MultiContentEntryText(
                pos=(xBubble, 0), size=(bubbleWidth, height), font=0, flags=RT_HALIGN_CENTER | RT_VALIGN_CENTER, text=" ",
                backcolor=_bubble_bg, backcolor_sel=_bubble_bg))
        _fore_color = getattr(self, "foreColor", getattr(self, "foregroundColor", getattr(self, "fore_color", None)))
        try:
            res.append(MultiContentEntryText(
                pos=(xBubble + _padding - 1, 0), size=(textWidth + 2, height), font=0,
                flags=RT_HALIGN_CENTER | RT_VALIGN_CENTER | RT_BLEND, text=text, color=_fore_color, color_sel=_fore_color,
                textBWidth=1, textBColor=0x010101))
        except TypeError:
            res.append(MultiContentEntryText(
                pos=(xBubble + _padding - 1, 0), size=(textWidth + 2, height), font=0,
                flags=RT_HALIGN_CENTER | RT_VALIGN_CENTER | RT_BLEND, text=text, color=_fore_color, color_sel=_fore_color))
        if currentPage < pageCount and self.picShevronRight:
            res.append(MultiContentEntryPixmapAlphaBlend(
                pos=(xBubble + bubbleWidth + self.spacing, 0), size=(pixdWidth, pixdHeight), png=self.picShevronRight,
                backcolor=None, backcolor_sel=None, flags=BT_ALIGN_CENTER))
        return res
