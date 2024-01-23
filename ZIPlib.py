import csv
import ZIPimg

IRS_PREFIXES = [
    "005",  # Holtsville, NY
    "055",  # Andover, MA
    "192",  # Philadelphia, PA
    "375",  # Memphis, TN
    "399",  # Atlanta, GA
    "459",  # Cincinnati, OH
    "649",  # Kansas City, MO
    "733",  # Austin, TX
    "842",  # Ogden, UT
    "928",  # Fresno, CA
]
MILIARTY_PREFIXES = [
    "09",  #
    "962",  # Korea
    "963",  # Japan
    "964",  # Philippines
    "965",  # Pacific & Antarctic bases
    "966",  # Naval/Marine
]
STATE_ABBR_MAP = {
    "AL": "Alabama",
    "AK": "Alaska",
    "AZ": "Arizona",
    "AR": "Arkansas",
    "CA": "California",
    "CO": "Colorado",
    "CT": "Connecticut",
    "DE": "Delaware",
    "DC": "District of Columbia",
    "FL": "Florida",
    "GA": "Georgia",
    "HI": "Hawaii",
    "ID": "Idaho",
    "IL": "Illinois",
    "IN": "Indiana",
    "IA": "Iowa",
    "KS": "Kansas",
    "KY": "Kentucky",
    "LA": "Louisiana",
    "ME": "Maine",
    "MD": "Maryland",
    "MA": "Massachusetts",
    "MI": "Michigan",
    "MN": "Minnesota",
    "MS": "Mississippi",
    "MO": "Missouri",
    "MT": "Montana",
    "NE": "Nebraska",
    "NV": "Nevada",
    "NH": "New Hampshire",
    "NJ": "New Jersey",
    "NM": "New Mexico",
    "NY": "New York",
    "NC": "North Carolina",
    "ND": "North Dakota",
    "OH": "Ohio",
    "OK": "Oklahoma",
    "OR": "Oregon",
    "PA": "Pennsylvania",
    "RI": "Rhode Island",
    "SC": "South Carolina",
    "SD": "South Dakota",
    "TN": "Tennessee",
    "TX": "Texas",
    "UT": "Utah",
    "VT": "Vermont",
    "VA": "Virginia",
    "WA": "Washington",
    "WV": "West Virginia",
    "WI": "Wisconsin",
    "WY": "Wyoming",
}


"""
Human readable string representation of STATE_ABBR_MAP. In the form "ST-State."
"""


def state_abbrs_str():
    out_str = ""
    for abbr in STATE_ABBR_MAP:
        out_str += abbr + "-" + STATE_ABBR_MAP[abbr] + "\n"
    return out_str[:-1] if len(out_str) >= 1 else ""


"""
Loads the ZIP codes from the ZIP code database. Must be called before other methods using computed ZIP codes or prefixes may be used
"""


def load_ZIPs(filename="zip_code_database.csv", disallowed_prefixes=[]):
    __singleton_instance.load_ZIPs(filename, disallowed_prefixes)


"""
Gets the ZIP object with the ZIP code passed in. A new ZIP will be created with just the code if none was found
"""


def get_ZIP(ZIP_code):
    return __singleton_instance.find_ZIP(ZIP_code)


def is_ZIP_prefixes(zip):
    return __singleton_instance.is_ZIP_prefixed(zip)


def get_hull(prefix):
    return __singleton_instance.get_hull(prefix)


def get_all_ZIPs():
    return __singleton_instance.ZIPs[:]


"""
ZIP class with named properties pulled from individual lines in the ZIP code database
"""


class ZIP:
    def __init__(self, row):
        self.ZIP_code = ZIP.__read_remove_value(row, "zip")
        self.type = ZIP.__read_remove_value(row, "type")
        self.decommissioned = (
            True
            if ZIP.__read_remove_value(row, "decommissioned", "0") == "1"
            else False
        )
        self.primary_city = ZIP.__read_remove_value(row, "primary_city")
        self.acceptable_cities = ZIP.__read_remove_value(row, "acceptable_cities")[
            1:-2
        ].split(",")
        self.unacceptable_cities = ZIP.__read_remove_value(row, "unacceptable_cities")[
            1:-2
        ].split(",")
        self.state_abbr = ZIP.__read_remove_value(row, "state")
        self.county = ZIP.__read_remove_value(row, "county")
        self.timezone = ZIP.__read_remove_value(row, "timezone")
        self.area_codes = ZIP.__read_remove_value(row, "area_codes")
        self.world_region = ZIP.__read_remove_value(row, "world_region")
        self.country = ZIP.__read_remove_value(row, "country")
        self.latitude = float(ZIP.__read_remove_value(row, "latitude", "0.0"))
        self.longitude = float(ZIP.__read_remove_value(row, "longitude", "0.0"))
        self.irs_estimated_population = int(
            ZIP.__read_remove_value(row, "irs_estimated_population", "0")
        )
        self.other_vals = row

    """
	Returns the full state name where this ZIP code belongs
	"""

    def state_name(self):
        if self.state_abbr in STATE_ABBR_MAP:
            return STATE_ABBR_MAP[self.state_abbr]
        return self.state_abbr

    """
	Returns the name of the region of the US where the ZIP code is located. 
	This is solely determined by the first digit of the ZIP code.
	"""

    def get_region_name(self):
        region = int(self.ZIP_code[0])
        if region == 0:
            return "New England"
        if region == 1:
            return "Mid Atlantic"
        if region == 2:
            return "South Atlantic"
        if region == 3:
            return "Deep South"
        if region == 4:
            return "Eastern Midwest"
        if region == 5:
            return "North-Western Midwest"
        if region == 6:
            return "South-Western Midwest"
        if region == 7:
            return "Western South"
        if region == 8:
            return "Rockies"
        if region == 9:
            return "Pacific"
        return ""

    """
	Method to read and remove a key value from the dictionary passed in.
	If no value exists, an empty string is returned
	"""

    @staticmethod
    def __read_remove_value(dict, key, default_value=""):
        value = default_value
        if key in dict:
            value = dict[key]
            del dict[key]
        return value


"""
Class that contains a lot of the more complex ZIP code calcuations. There only needs to be one at a time, so consumers won't have direct access to this class.
"""


class __ZIPlib:

    """
    Reading the data requires parameters, but this class inits immediately. The load_ZIPs method needs to be called.
    """

    def __init__(self):
        self.ZIPs = []
        self.prefixes = {}

    """
	Reads ZIP codes and populates the ZIPs and prefixes properties Does not compute hulls. Those are done as needed.
	"""

    def load_ZIPs(self, filename, disallowed_prefixes):
        if len(self.ZIPs) > 0:
            return
        self.__read_parse_ZIPs(filename)
        self.__cull_entries(disallowed_prefixes)
        self.__group_all_prefixes()

    """
	Given a ZIP code, finds its corresponding ZIP object, or creates a new one. The new object will not be inserted into the ZIPs property
	"""

    def find_ZIP(self, ZIP_code):
        if ZIP_code[:3] in self.prefixes: 
            for zip in self.prefixes[ZIP_code[:3]]["ZIPs"]:
                if zip.ZIP_code == ZIP_code:
                    return zip
        return ZIP({"zip": ZIP_code})

    """
	Directly handles reading the ZIP codes and converts them to ZIP objects
	"""

    def __read_parse_ZIPs(self, filename="zip_code_database.csv"):
        self.ZIPs = []
        with open(filename) as ZIPFile:
            ZIPReader = csv.DictReader(ZIPFile)
            for row in ZIPReader:
                self.ZIPs.append(ZIP(row))

    """
	Removes all ZIP objects from the ZIPs property that should not be included
	"""

    def __cull_entries(self, disallowed_prefixes):
        indexesToDelete = []
        for i in range(0, len(self.ZIPs)):
            if self.__should_be_culled(self.ZIPs[i], disallowed_prefixes):
                indexesToDelete.append(i)
        for index in reversed(indexesToDelete):
            del self.ZIPs[index]

    """
	Checks if a ZIP object should be included in the ZIP library calculations
	"""

    def __should_be_culled(self, zip, diallowed_prefixes):
        if zip.decommissioned:
            return True
        if zip.state_abbr not in STATE_ABBR_MAP:
            return True
        if self.__zip_any_prefix(diallowed_prefixes, zip):
            return True
        if self.__zip_any_prefix(IRS_PREFIXES + MILIARTY_PREFIXES, zip):
            return True

        return False

    """
	Given a list of prefixes, determines if the ZIP code of a ZIP object uses any of those prefixes
	"""

    def __zip_any_prefix(self, prefixes, zip):
        for prefix in prefixes:
            if self.is_ZIP_prefixed(prefix, zip):
                return True
        return False

    """
	Determines if the ZIP code of a ZIP object starts with a specific prefix.
	"""

    def is_ZIP_prefixed(self, prefix, zip):
        return zip.ZIP_code[: len(prefix)] == prefix

    """
	populates the self.prefixes index with all 1-, 2-, and 3-digit prefixes.
	"""

    def __group_all_prefixes(self):
        self.__group_prefixes(1)
        self.__group_prefixes(2)
        self.__group_prefixes(3)

    """
	populates the self.prefixes index with all num_digits length prefixes.
	"""

    def __group_prefixes(self, num_digits):
        for zip in self.ZIPs:
            if zip.ZIP_code[:3] == "569":
                continue  # parcel return in DC, not upper midwest
            if zip.ZIP_code == "88888":
                continue  # North Pole, not Rockies
            if float(zip.latitude) == 0:
                continue
            if float(zip.longitude) == 0:
                continue

            prefix_digits = zip.ZIP_code[:num_digits]
            if prefix_digits in self.prefixes:
                self.prefixes[prefix_digits]["ZIPs"].append(zip)
            else:
                self.prefixes[prefix_digits] = {"ZIPs": [zip]}

    """
	Computes/stores or fetches the convex hull approximation for the prefix passed as a list of {'lattitude','longitude'} dictionaries.
	"""

    def get_hull(self, prefix):
        if prefix not in self.prefixes:
            return []
        if "hull" not in self.prefixes[prefix]:
            self.__compute_convex_hull(prefix)
        return self.prefixes[prefix]["hull"]

    """
	Computes the convex hull approximation for the prefix passed in
	"""

    def __compute_convex_hull(self, prefix):
        self.prefixes[prefix]["ZIPs"] = sorted(
            self.prefixes[prefix]["ZIPs"], key=lambda zip: zip.latitude
        )

        cmp_top = lambda zip1, zip2: float(zip1.longitude) > float(zip2.longitude)
        cmp_bottom = lambda zip1, zip2: float(zip1.longitude) < float(zip2.longitude)

        top_hull = self.__compute_hull(self.prefixes[prefix]["ZIPs"], cmp_top)
        bottom_hull = self.__compute_hull(self.prefixes[prefix]["ZIPs"], cmp_bottom)

        self.prefixes[prefix]["hull"] = top_hull + list(reversed(bottom_hull[1:-1]))

    """
	Computes either the top or bottom half of the convex hull approximation, based on the longitude cmp given.
	"""

    def __compute_hull(self, sorted_zips, cmp):
        hull = []
        peak_i = 0

        for zip in sorted_zips:
            if zip.state_abbr == 'AK' or zip.state_abbr == 'HI': continue
            if (
                len(hull) > 0
                and zip.latitude == hull[-1].latitude
                and zip.longitude == hull[-1].longitude
            ):
                continue

            while len(hull) - 1 > peak_i and cmp(zip, hull[-1]):
                del hull[-1]

            if (
                len(hull) == 0
                or cmp(zip, hull[peak_i])
                or (
                    zip.longitude == hull[peak_i].longitude
                    and zip.latitude != hull[peak_i].latitude
                )
            ):
                peak_i = len(hull)

            hull.append(zip)

        return hull


__singleton_instance = __ZIPlib()
