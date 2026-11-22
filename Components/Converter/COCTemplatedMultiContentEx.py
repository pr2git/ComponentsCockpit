# Copyright (C) 2018-2026 by xcentaurix
# License: GNU General Public License v3.0


# Backport of OpenViX's Components/Converter/TemplatedMultiContentEx.py, renamed
# with the COC prefix used by this plugin's own converters. openATV does not
# ship this converter at all; shipping our own copy lets skins use it on both
# forks - functionally identical to OpenViX's native TemplatedMultiContentEx.


from enigma import eListbox
from Components.Converter.TemplatedMultiContent import TemplatedMultiContent
from Components.Converter.StringList import StringList


class COCTemplatedMultiContentEx(TemplatedMultiContent):
    """TemplatedMultiContent with e (item width) and c (item horizontal center) available in the template."""

    def __init__(self, args):
        self._raw_args = args
        self._size_resolved = False
        StringList.__init__(self, args)
        # Everything imported/assigned below exists only to populate the eval()
        # namespace a few lines down - the skin-authored template string (e.g.
        # gFont(...), MultiContentEntryText(...), BT_SCALE, e, c) references
        # these names directly, but pylint/flake8 can't see usage through eval().
        from enigma import (  # noqa: F401  pylint: disable=possibly-unused-variable
            BT_SCALE, BT_KEEP_ASPECT_RATIO, BT_ALPHATEST, BT_ALPHABLEND,
            BT_FIXRATIO, BT_HALIGN_LEFT, BT_HALIGN_CENTER, BT_HALIGN_RIGHT,
            BT_VALIGN_TOP, BT_VALIGN_CENTER, BT_VALIGN_BOTTOM, BT_ALIGN_CENTER,
            RT_HALIGN_CENTER, RT_HALIGN_LEFT, RT_HALIGN_RIGHT, RT_VALIGN_BOTTOM,
            RT_VALIGN_CENTER, RT_VALIGN_TOP, RT_WRAP, RT_BLEND,
            eListboxPythonMultiContent, gFont)

        from Components.MultiContent import (  # noqa: F401  pylint: disable=possibly-unused-variable
            MultiContentEntryPixmap, MultiContentEntryPixmapAlphaBlend,
            MultiContentEntryPixmapAlphaTest, MultiContentEntryProgress,
            MultiContentEntryProgressPixmap, MultiContentEntryText,
            MultiContentTemplateColor)

        try:
            from Components.MultiContent import (  # noqa: F401  pylint: disable=possibly-unused-variable
                MultiContentEntryPixmapAlphaBlendScaled, MultiContentEntryPixmapAlphaTestScaled)
        except ImportError:
            # openATV 6.4 and earlier don't have the Scaled variants; define
            # them as aliases to the non-scaled variants so skin templates that
            # use them still work on those versions.
            MultiContentEntryPixmapAlphaBlendScaled = MultiContentEntryPixmapAlphaBlend
            MultiContentEntryPixmapAlphaTestScaled = MultiContentEntryPixmapAlphaTest

        try:
            from Components.MultiContent import (  # noqa: F401  pylint: disable=possibly-unused-variable
                MultiContentEntryLinearGradient, MultiContentEntryLinearGradientAlphaBlend)
        except ImportError:
            MultiContentEntryLinearGradient = None  # noqa: F841  pylint: disable=possibly-unused-variable
            MultiContentEntryLinearGradientAlphaBlend = None  # noqa: F841  pylint: disable=possibly-unused-variable

        from skin import parseFont, getSkinFactor  # noqa: F401  pylint: disable=possibly-unused-variable

        f = getSkinFactor()  # noqa: F841  pylint: disable=possibly-unused-variable
        e = 0  # noqa: F841  pylint: disable=possibly-unused-variable
        c = 0  # noqa: F841  pylint: disable=possibly-unused-variable
        i = int  # noqa: F841  pylint: disable=possibly-unused-variable
        loc = locals()
        del loc["self"]
        del loc["args"]
        self._eval_locals = loc
        # openATV's TemplatedMultiContent tracks this as self.activeStyle (camelCase);
        # OpenViX's tracks it as self.active_style (snake_case). Set both so whichever
        # this fork's base class actually reads is correctly initialized.
        self.active_style = None
        self.activeStyle = None
        self.template = eval(args, {}, loc)  # pylint: disable=eval-used
        self.scale = None
        self.orientations = {
            "orHorizontal": getattr(eListbox, "orHorizontal", 0),
            "orVertical": getattr(eListbox, "orVertical", 1),
            "orGrid": getattr(eListbox, "orGrid", getattr(eListbox, "orVertical", 1)),
        }
        assert "fonts" in self.template
        assert "itemHeight" in self.template
        assert "template" in self.template or "templates" in self.template
        assert "template" in self.template or "default" in self.template["templates"]
        if "template" not in self.template:
            templateDefault = self.template["templates"]["default"]
            self.template["template"] = templateDefault[1]
            self.template["itemHeight"] = templateDefault[0]
            if len(templateDefault) > 2:
                self.template["selectionEnabled"] = templateDefault[2]
            if len(templateDefault) > 3:
                self.template["scrollbarMode"] = templateDefault[3]
            if len(templateDefault) > 5:
                self.template["itemWidth"] = templateDefault[4]
                self.template["orientation"] = templateDefault[5]

    def _resolveWidth(self):
        # OpenViX's own changed() confirms self.master is the renderer there
        # (isinstance(self.master, Listbox)); openATV's own changed() instead
        # reads self.downstream_elements[0] for the same purpose. Try both so
        # this works regardless of which fork's convention actually applies.
        candidates = [getattr(self, "master", None)]
        try:
            candidates.extend(self.downstream_elements or [])
        except Exception:
            pass
        for candidate in candidates:
            try:
                instance = getattr(candidate, "instance", None)
                if instance is not None:
                    width = instance.size().width()
                    if width > 0:
                        return width
            except Exception:
                continue
        return None

    def _tryResolveTemplate(self):
        if self._size_resolved:
            return
        width = self._resolveWidth()
        if width:
            self._eval_locals["e"] = width
            self._eval_locals["c"] = width // 2
            self.template = eval(self._raw_args, {}, self._eval_locals)  # pylint: disable=eval-used
            self._size_resolved = True
            # force parent to re-apply the now-correctly-sized template
            self.active_style = None
            self.activeStyle = None

    def changed(self, what):
        # openATV's TemplatedMultiContent.changed() applies self.template via a
        # private nested function - it never calls a self.setTemplate() hook,
        # so setTemplate() below is dead code on that fork. Resolving the width
        # here instead, before delegating to the parent, works on both forks.
        self._tryResolveTemplate()
        TemplatedMultiContent.changed(self, what)

    def setTemplate(self):
        # Reached on OpenViX, whose own changed() calls self.setTemplate() directly.
        self._tryResolveTemplate()
        TemplatedMultiContent.setTemplate(self)
