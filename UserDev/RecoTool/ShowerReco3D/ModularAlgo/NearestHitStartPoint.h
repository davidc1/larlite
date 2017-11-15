/**
 * \file NearestHitStartPoint.h
 *
 * \ingroup ModularAlgo
 *
 * \brief Class def header for a class NearestHitStartPoint
 *
 * @author David Caratelli
 */

/** \addtogroup ModularAlgo

    @{*/
#ifndef NEARESTHITSTARTPOINT_H
#define NEARESTHITSTARTPOINT_H

#include <iostream>
#include "ShowerRecoModuleBase.h"
/**
   \class ShowerRecoModuleBase
   User defined class ShowerRecoModuleBase ... these comments are used to generate
   doxygen documentation!
 */
namespace showerreco {

class NearestHitStartPoint : ShowerRecoModuleBase {

public:

  /// Default constructor
  NearestHitStartPoint() {_name = "NearestHitStartPoint"; }

  /// Default destructor
  ~NearestHitStartPoint() {}

  /// Inherited/overloaded function from ShowerRecoModuleBase
  void do_reconstruction(const ::protoshower::ProtoShower &, Shower_t &);

};

} // showerreco

#endif
/** @} */ // end of doxygen group

