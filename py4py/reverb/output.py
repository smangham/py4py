"""
Reverberation Mapping module

This contains the type used to create and manipulate reverberation maps from Python output files.
"""
# -*- coding: utf-8 -*-
# pylint: disable=C0301
import numpy as np
from typing import List, Optional
from py4py.reverb import TransferFunction


def do_tf_plots(
    tf_list_inp: List[TransferFunction], dynamic_range: Optional[float] = None,
    keplerian: Optional[dict] = None, name: Optional[str] = None,
    file: Optional[str] = None, threshold: float = 0.8
):
    """
    Produces plots of the transfer functions for a list of provided TFs,
    with matching plotted dynamic ranges and name structures, and

    Args:
        tf_list_inp (List[TransferFunction]):
        dynamic_range (Optional[float]):
        keplerian (Optional[dict]):
        name (Optional[str]):
        file (Optional[str]):
        threshold (float):

    Todo:
        This should be in a separate folder
    """
    tf_delay: List[float] = []
    for tf_inp in tf_list_inp:
        tf_inp.plot(velocity=True, keplerian=keplerian, log=False, name=name)
        tf_inp.plot(
            velocity=True, keplerian=keplerian, log=True,
            name=('log' if name is None else name+"_log"), dynamic_range=dynamic_range
        )
        tf_delay.append(tf_inp.delay(threshold=threshold))

    if file is not None:
        print("Saving centroid transfer function delays to file: {}".format(file+"_tf_delay.txt"))
        np.savetxt(file+"_tf_delay.txt", np.array(tf_delay, dtype='float'), header="Delay")


def do_rf_plots(
    tf_min: TransferFunction, tf_mid: TransferFunction, tf_max: TransferFunction,
    keplerian: Optional[dict] = None, name: Optional[str] = None, file: Optional[str] = None
):
    """
    Do response plot for a TF

    Args:
        tf_min (TransferFunction):
        tf_mid (TransferFunction):
        tf_max (TransferFunction):
        keplerian (Optional[dict]):
        name (Optional[dict]):
        file (Optional[dict]):

    Todo:
        This should be in a separate folder
    """
    if name is not None:
        name += '_'
    else:
        name = ''

    total_min: float = np.sum(tf_min._emissivity).item()
    total_mid: float = np.sum(tf_mid._emissivity).item()
    total_max: float = np.sum(tf_max._emissivity).item()

    calibration_factor: float = total_mid / ((total_min + total_max) / 2.0)

    tf_mid.response_map_by_tf(tf_min, tf_max, cf_low=1.0, cf_high=1.0).plot(
        velocity=True, response_map=True, keplerian=keplerian, name=name+"resp_mid"
    )
    rf_mid = tf_mid.delay(response=True, threshold=0.8)

    tf_mid.response_map_by_tf(tf_min, tf_mid, cf_low=calibration_factor, cf_high=1.0).plot(
        velocity=True, response_map=True, keplerian=keplerian, name=name+"resp_low"
    )
    rf_min = tf_mid.delay(response=True, threshold=0.8)
    tf_mid.response_map_by_tf(tf_mid, tf_max, cf_low=1.0, cf_high=calibration_factor).plot(
        velocity=True, response_map=True, keplerian=keplerian, name=name+"resp_high"
    )
    rf_max = tf_mid.delay(response=True, threshold=0.8)

    if file is not None:
        print("Saving RF plots to file: {}".format(file+"_rf_delay.txt"))
        np.savetxt(file+"_rf_delay.txt", np.array([rf_min, rf_mid, rf_max], dtype='float'), header="Delay")
