#!/bin/bash
I18NDUDE=~/Plone/zinstance/bin/i18ndude

### Grab new translated strings
# tx pull -a

# Flush the english (transifex source language) po files
# If we don't do this, new *-manual translations won't be synced.
> en/LC_MESSAGES/bika.po
> en/LC_MESSAGES/plone.po

find . -name "*.mo" -delete

### bika domain
### ===========
$I18NDUDE rebuild-pot --pot i18ndude.pot --exclude "build" --create bika ..
$I18NDUDE filter i18ndude.pot bika-health.pot > bika-tmp.pot
msgcat --strict --use-first bika-health.pot bika-manual.pot bika-tmp.pot > bika.pot
$I18NDUDE sync --pot bika.pot */LC_MESSAGES/bika.po
rm i18ndude.pot bika-tmp.pot

### plone domain
### ============
PLONE_POT=~/Plone/zinstance/parts/omelette/plone/app/locales/locales/plone.pot
$I18NDUDE rebuild-pot --pot i18ndude.pot --create plone ../profiles/
$I18NDUDE filter i18ndude.pot bika-health.pot > plone-tmp.pot
$I18NDUDE filter plone-tmp.pot $PLONE_POT > i18ndude.pot
msgcat --strict --use-first bika-health.pot plone-manual.pot i18ndude.pot > plone.pot
$I18NDUDE sync --pot plone.pot */LC_MESSAGES/plone.po
rm i18ndude.pot plone-tmp.pot

for po in `find . -name "*.po"`; do msgfmt -o ${po/%po/mo} $po; done

### push new strings to transifex
# tx push -s -t
