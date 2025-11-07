from panphon.distance import Distance

import os
import importlib.resources as pkg_resources
from panphon import featuretable

# Patch featuretable to look up the correct data path
if not hasattr(featuretable, "_original_read_bases"):
    featuretable._original_read_bases = featuretable.FeatureTable._read_bases

    def _fixed_read_bases(self, fn, weights):
        # If PanPhon can't find its data file, use the installed version
        if not os.path.exists(fn):
            try:
                fn = pkg_resources.files("panphon.data").joinpath("ipa_all.csv")
            except Exception:
                fn = os.path.join(os.path.dirname(featuretable.__file__), "data", "ipa_all.csv")
        return featuretable._original_read_bases(self, fn, weights)

    featuretable.FeatureTable._read_bases = _fixed_read_bases

# Now import Distance normally
from panphon.distance import Distance

d = Distance()
print(d.feature_edit_distance('p', 'b'))


print(Distance().feature_edit_distance('p','b'))