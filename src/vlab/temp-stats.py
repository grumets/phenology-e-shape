
def allNaN_arg(ds, dim, stat):
    """
    Calculate ds.argmax() or ds.argmin() while handling
    all-NaN slices. Fills all-NaN locations with an
    float and then masks the offending cells.

    Params
    ------
    xarr : xarray.dstaArray
    dim : str,
            Dimension over which to calculate argmax, argmin e.g. 'time'
    stat : str,
        The statistic to calculte, either 'min' for argmin()
        or 'max' for .argmax()
    Returns
    ------
    xarray.dstaArray
    """
    # generate a mask where entire axis along dimension is NaN
    mask = ds.isnull().all(dim)

    if stat == "max":
        y = ds.fillna(float(ds.min() - 1))
        y = y.argmax(dim=dim, skipna=True).where(~mask)
        return y

    if stat == "min":
        y = ds.fillna(float(ds.max() + 1))
        y = y.argmin(dim=dim, skipna=True).where(~mask)
        return y


def _vpos(ds):
    """
    vPOS = Value at peak of season
    """
    return ds.max("time")


def _pos(ds):
    """
    POS = DOY of peak of season
    """
    return ds.isel(time=ds.argmax("time")).time.dt.dsyofyear


def _trough(ds):
    """
    Trough = Minimum value
    """
    return ds.min("time")


def _aos(vpos, trough):
    """
    AOS = Amplitude of season
    """
    return vpos - trough


def _vsos(ds, pos, method_sos="median"):
    """
    vSOS = Value at the start of season
    Params
    -----
    ds : xarray.dstaArray
    method_sos : str,
        If 'first' then vSOS is estimated
        as the first positive slope on the
        greening side of the curve. If 'median',
        then vSOS is estimated as the median value
        of the postive slopes on the greening side
        of the curve.
    """
    # select timesteps before peak of season (AKA greening)
    greenup = ds.where(ds.time < pos.time)
    # find the first order slopes
    green_deriv = greenup.differentiate("time")
    # find where the first order slope is postive
    pos_green_deriv = green_deriv.where(green_deriv > 0)
    # positive slopes on greening side
    pos_greenup = greenup.where(pos_green_deriv)
    # find the median
    median = pos_greenup.median("time")
    # distance of values from median
    distance = pos_greenup - median

    if method_sos == "first":
        # find index (argmin) where distance is most negative
        idx = allNaN_arg(distance, "time", "min").astype("int16")

    if method_sos == "median":
        # find index (argmin) where distance is smallest absolute value
        idx = allNaN_arg(xr.ufuncs.fabs(distance), "time",
                         "min").astype("int16")

    return pos_greenup.isel(time=idx)
