import webingo.support as support
import webingo.wallet.denominations as denoms
import webingo.jackpot.config as jpconfig

POT_KEY_PREFIX = "POT__"
POT_KEY_DENOM_SUFFIX = "__DENOM"
POT_KEY_MIN_SUFFIX = "__MIN"
POT_KEY_MAX_SUFFIX = "__MAX"
POT_KEY_STORAGE_MULTIPLIER_SUFFIX = "__SMUL"

class pot:

    def __init__(self, site_id, id):
        defaults = jpconfig.get_jackpot_defaults()

        self.id = id
        self.site_id = site_id

        self.db = support.get_db()
        self.db_key_base = POT_KEY_PREFIX + str(site_id) + "__" + str(id)
        self.storage_int_multiplier = int(defaults["storage_int_multiplier"])

        self.denom = defaults["denomination"]
        self.value_min = defaults["min_value"] * self.storage_int_multiplier
        self.value_max = defaults["max_value"] * self.storage_int_multiplier
        self.load(True) # load configs and value

        self._validate(False, True)

    def inc( self, credit_fractional ):
        to_add = int(credit_fractional * self.storage_int_multiplier)
        self.db.incrby( self.db_key_base, to_add )
        self._value += to_add
        self._validate( False, True )

    def _validate( self, reload = True, save_if_inconsistent = False ):
        if reload:
            self.load()

        inconsistent = False

        if not hasattr(self, "_value"):
            self._value = self.value_min
            inconsistent = True
        elif self._value > self.value_max:
            self._value = self.value_max
            inconsistent = True
        elif self._value < self.value_min:
            self._value = self.value_min
            inconsistent = True

        if save_if_inconsistent and inconsistent:
            self.save()

    def pay_fraction( self, fraction ):
        if (not fraction) or fraction < 0.0 or fraction > 1.0:
            raise ValueError("Illegal fraction for jackpot payout: " + str(fraction))

        self.load()
        self.inc( -fraction * self.value() )

    def pay_value( self, v ):
        if v > self.value():
            raise ValueError("Attempted to pay more than we can: " + str(v))

        self.load()
        self.inc( -v )


    def load( self, configs = False ):
        if configs:
            mult = self.db.get(self.db_key_base + POT_KEY_STORAGE_MULTIPLIER_SUFFIX)
            if mult != None:
                self.storage_int_multiplier = int(mult)
            minval = self.db.get(self.db_key_base + POT_KEY_MIN_SUFFIX)
            if minval != None:
                self.value_min = int(minval) * self.storage_int_multiplier
            maxval = self.db.get(self.db_key_base + POT_KEY_MAX_SUFFIX)
            if maxval != None:
                self.value_max = int(maxval) * self.storage_int_multiplier
            denom = self.db.get(self.db_key_base + POT_KEY_DENOM_SUFFIX)
            if denom != None:
                self.denom = str(denom)

        existing = self.db.get(self.db_key_base)
        self._value = int(existing) if existing else self.value_min

    def save( self ):
        self.db.set(self.db_key_base, self._value)

    def save_configs( self ):
        self.db.set(self.db_key_base + POT_KEY_STORAGE_MULTIPLIER_SUFFIX,
                    self.storage_int_multiplier)
        self.db.set(self.db_key_base + POT_KEY_MIN_SUFFIX,
                    int(self.value_min / self.storage_int_multiplier))
        self.db.set(self.db_key_base + POT_KEY_MAX_SUFFIX,
                    int(self.value_max / self.storage_int_multiplier))
        self.db.set(self.db_key_base + POT_KEY_DENOM_SUFFIX,
                    self.denom)

    def value( self ) -> float:
        return (self._value / float(self.storage_int_multiplier)) if self._value else float(0)

    def set_value( self, val ):
        self._value = int(val*self.storage_int_multiplier)
        self._validate()
        self.save()
