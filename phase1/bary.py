"""Barycentric conversion for the H1 confirmatory run (prereg_h1.md
Section 2.2): topocentric UTC -> BJD_TDB with solar-system ephemeris DE440
and observatory ITRF coordinates.

Observatory locations come from the astropy sites registry where present
(FAST, Effelsberg, Nancay, CHIME, Parkes, ...); campaigns at observatories
absent from the registry use the frozen supplementary coordinates below
(recorded with provenance in phase0/environment_pin.json at pinning time).
Observatory-position error bounds the conversion error by the Earth-radius
light-crossing time (~21 ms), four orders below the sigma_v,min = 60 s
visit scale; the supplementary values are all far better than that.
"""

import astropy.units as u
from astropy.coordinates import (EarthLocation, SkyCoord,
                                 solar_system_ephemeris)
from astropy.time import Time

EPHEMERIS = "de440"

# Frozen supplementary ITRF coordinates (meters) for observatories absent
# from the astropy sites registry. Sources: NRAO SCHED locations.dat
# (GSF2016a solution unless noted); Stockert from the published geodetic
# position (50.5700 N, 6.7233 E, 435 m).
SUPPLEMENTARY_XYZ_M = {
    # TMRT / Tianma 65-m (SCHED DBNAME TIANMA65, GSF2016a)
    "tianma65": (-2826708.6476, 4679237.0665, 3274667.5514),
    # Torun 32-m (SCHED DBNAME TORUN, ITRF2000)
    "torun": (3638558.5100, 1221969.7200, 5077036.7600),
    # Onsala 25-m "O8" (SCHED DBNAME ONSALA85, GSF2016a)
    "onsala85": (3370965.8787, 711466.1978, 5349664.2006),
    # Westerbork: campaign used single dish RT-1; SCHED lists RT0 (adjacent
    # dish, ~150 m away -> < 1 us timing effect). RT0 recorded as proxy.
    "westerbork_rt1": (3828767.2647, 442446.1739, 5064921.5700),
}

_STOCKERT_GEODETIC = (6.7233, 50.5700, 435.0)   # lon_deg_E, lat_deg_N, h_m


def get_location(name):
    """Resolve an observatory name: supplementary table first (frozen),
    then the astropy sites registry."""
    key = name.lower()
    if key in SUPPLEMENTARY_XYZ_M:
        x, y, z = SUPPLEMENTARY_XYZ_M[key]
        return EarthLocation.from_geocentric(x * u.m, y * u.m, z * u.m)
    if key == "stockert":
        lon, lat, h = _STOCKERT_GEODETIC
        return EarthLocation.from_geodetic(lon * u.deg, lat * u.deg,
                                           h * u.m)
    return EarthLocation.of_site(name)


def topo_utc_to_bjd_tdb(mjd_utc, location, ra_deg, dec_deg):
    """Topocentric MJD(UTC) -> barycentric MJD(TDB) at infinite frequency
    (dispersion handled separately per prereg 2.2). Accepts scalars or
    arrays."""
    t = Time(mjd_utc, format="mjd", scale="utc", location=location)
    target = SkyCoord(ra=ra_deg * u.deg, dec=dec_deg * u.deg)
    with solar_system_ephemeris.set(EPHEMERIS):
        ltt = t.light_travel_time(target, kind="barycentric")
    return (t.tdb + ltt).mjd
