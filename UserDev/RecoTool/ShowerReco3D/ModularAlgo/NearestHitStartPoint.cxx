#ifndef NEARESTHITSTARTPOINT_CXX
#define NEARESTHITSTARTPOINT_CXX

#include "NearestHitStartPoint.h"

#include "LArUtil/Geometry.h"
#include "LArUtil/GeometryHelper.h"
#include "LArUtil/DetectorProperties.h"

namespace showerreco {

  void NearestHitStartPoint::do_reconstruction( const ::protoshower::ProtoShower & proto_shower,
					      Shower_t& resultShower)
{

    auto geom  = larutil::Geometry::GetME();
    auto geomH = larutil::GeometryHelper::GetME();
  
    //if the module does not have 2D cluster info -> fail the reconstruction
    if (!proto_shower.hasCluster2D()) {
        std::stringstream ss;
        ss << "Fail @ algo " << this->name() << " due to missing 2D cluster";
        throw ShowerRecoException(ss.str());
    }

    // get the proto-shower 3D vertex
    auto const& vtx3D_v = proto_shower.vertexes();
    
    // are there many vertices? if more than 1 this algo does not know what to do
    if (vtx3D_v.size() != 1){
      std::cout << "Number of vertices is " << vtx3D_v.size() << " is not one!" << std::endl;
      return;
    }

    // take the vtx for the neutrino interaction
    auto const& vtx = vtx3D_v[0];

    auto & clusters = proto_shower.params();

    // STEP 1:
    // given the shower's reconstructed 3D direction vector
    // find the collection-plane closest to it
    // this will be the 2D collection-plane start point

    ::larutil::Point2D strtpt0;
    size_t clus_idx = 0;
    int    pl0 = 0;
    
    for (size_t i=0; i < clusters.size(); i++) {

      auto const& clus = clusters.at(i);

      // plane
      auto const& pl = clus.plane_id.Plane;

      if (pl != 2) continue;
      
      // project vertex onto this plane
      auto const& vtx2D = geomH->Point_3Dto2D(vtx,pl);

      // get the hits associated with this cluster
      auto const& hits = clus.hit_vector;

      // gind nearest hit to vtx2D:
      double sw, st;
      double d2Dmin = 10000.;
      for (auto const& hit : hits) {

	auto d2D = sqrt( (hit.w-vtx2D.w)*(hit.w-vtx2D.w)+(hit.t-vtx2D.t)*(hit.t-vtx2D.t) );

	if (d2D < d2Dmin) { d2Dmin = d2D; sw = hit.w; st = hit.t; }

      }

      std::cout << "start point @ plane " << pl << " @ " << sw << ", " << st << std::endl;
      
      clus_idx = i;
      pl0      = pl;
      strtpt0.w = sw;
      strtpt0.t = st;
      strtpt0.plane = pl;
      std::cout << "pxpoint for pl2 : " << sw << ", " << st << std::endl;
      
    }// for all clusters

    if (pl0 != 2) {
      std::stringstream ss;
      ss << "Fail @ algo " << this->name() << " due to missing Collection-Plane 2D cluster";
      throw ShowerRecoException(ss.str());
    }

    ::larutil::Point2D strtpt1;
    int pl1;
    bool found = false; // did we find start point coord. on 2nd plane?

    // find a plane that is not the one with the min start-vtx distance
    for (int p = 0; p < 3; p++) {

      if (p != pl0) {

	// project reconstructed 3D direction and vertex to this plane
	auto const& vtx2D   = geomH->Point_3Dto2D(vtx,p);
	auto const& dir3D   = resultShower.fDCosStart;
	auto const& slope2D = geomH->Slope_3Dto2D(dir3D,p);

	std::cout << "2D direction " << slope2D << std::endl;

	// the 2D vertex and slope give us the line
	// on which to search for the wire coordinate
	// for the 3D start point on this plane
	// to do so we know the time coordinate
	// from the previously found point "strtpt"
	// find where this time coordinate intersects the vtx -> slope line

	// wire coordinate of the start point on this plane
	double sw = ( strtpt0.t - vtx2D.t ) / slope2D + vtx2D.w;
	double st = strtpt0.t; // start point time is the same! duh...

	strtpt1.w = sw;
	strtpt1.t = st;

	if (sw / geom->WirePitch(0) >= geom->Nwires(p) ) continue;
	if (sw / geom->WirePitch(0) < 0                ) continue;

	pl1 = p;

	found = true;
	break;
	
      }// if "another" plane
      
    }// for all planes

    if (found == false) {
      std::stringstream ss;
      ss << "Fail @ algo " << this->name() << " did not find start point on 2nd plane";
      throw ShowerRecoException(ss.str());
    }

    // now take the 2 2D start points and reconstruct the 3D one

    double sY, sZ;

    int w0 = strtpt0.w / geom->WirePitch(0);
    int w1 = strtpt1.w / geom->WirePitch(0);

    std::cout << "w0 : " << w0 << std::endl;
    std::cout << "w1 : " << w1 << std::endl;

    // check start/end point range
    if ( (w0 < 0) or (w0 > geom->Nwires(pl0)) or
	 (w1 < 0) or (w1 > geom->Nwires(pl1)) ) {
      std::stringstream ss;
      ss << "Fail @ algo " << this->name() << " due to wires out of range";
      throw ShowerRecoException(ss.str());
    }

    if (_verbose)
      std::cout << "pl " << pl0 << " wire : " << w0
		<< "pl " << pl1 << " wire : " << w1 << std::endl;
    
    geom->IntersectionPoint( w0, w1, pl0, pl1, sY, sZ);

    // check if reconstructed start point is outside of TPC volume    
    if (geomH->ContainedYZ(sY, sZ) == false){
      std::stringstream ss;
      ss << "Fail @ algo " << this->name() << " due to start point reconstructed out of TPC bouns : [Y,Z] -> ["
	 << sY << ", " << sZ << " ]" ; 
      throw ShowerRecoException(ss.str());
    }

    resultShower.fXYZStart = { strtpt0.t, sY, sZ} ;

    //std::cout << "DONE " << std::endl << std::endl;
    
}

} //showerreco

#endif
