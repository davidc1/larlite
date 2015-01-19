#ifndef ERTOOL_ALGOLONELYE_CXX
#define ERTOOL_ALGOLONELYE_CXX

#include "AlgoLonelyE.h"

namespace ertool {

  AlgoLonelyE::AlgoLonelyE() : AlgoBase()
  {
    _name     = "AlgoLonelyE";
    _debug    = false;
  }

  void AlgoLonelyE::Reset()
  {}


  void AlgoLonelyE::ProcessBegin()
  {

    _alg_singleE.ProcessBegin();
    
    return;
  }

  void AlgoLonelyE::LoadParams(std::string fname, size_t version){

    _alg_singleE.LoadParams(fname,version);
    return;
  }

  ParticleSet AlgoLonelyE::Reconstruct(const EventData &data)
  { 

    // What is in this event?
    if (_debug){
      std::cout << "There are " << data.Shower().size() << " showers." << std::endl;
      std::cout << "There are " << data.Track().size() << " tracks." << std::endl << std::endl;
    }

    //Get a list of single (start point isolated) electron showers
    //from the AlgoSingleE instance
    ParticleSet single_es = _alg_singleE.Reconstruct(data);
    
    // create empty ParticleSet for the products
    ParticleSet lonely_es;
    
    // Run filter for every "single electron" found by previous step
    for(auto const& s : single_es) {

      // Convert shower into HalfLine
      if (_debug) { std::cout << "Shower Energy: " << s.Energy() << std::endl; }

      if ( isLonely(data.Shower(s.RecoObjID()), data) ) { lonely_es.push_back(s); }
    }// for all input showers from AlgoSingleE

    if (_debug) { std::cout << std::endl; }

    return lonely_es; 
  }


  bool AlgoLonelyE::isLonely(const Shower& s, const EventData& data) const
  {
    // holder to keep track of decision:
    // is this shower lonely?
    bool lonely = false;

    // flip the shower (we are interested in the direction bakwards
    geoalgo::HalfLine_t shrBack(s.Start(), s.Dir()*(-1));
    // Loop over tracks
    for (auto const& t : data.Track()) {
      if (_debug) { std::cout << "Track Energy: " << t->_energy << std::endl; }
      double distToTrack  = isShowerFromTrack( shrBack, *t );
    }

    // Loop over showers
    for (auto const& s2 : data.Shower()) {
      if( s.ID() == s2->ID() ) continue;
      if (_debug) { std::cout << "Shower Energy: " << s2->_energy << std::endl; }
    // flip the other shower (we are interested in the direction bakwards
      geoalgo::HalfLine_t sBack(s2->Start(), s2->Dir()*(-1));
      double distToShower = isShowerFromShower( shrBack, sBack);
    }
    
    return lonely;
  }


  double AlgoLonelyE::isShowerFromTrack(const geoalgo::HalfLine_t& shr, 
					const geoalgo::Trajectory_t& trk) const
  {

    // try and find showers that originate from tracks
    // 2 categories:
    // 1) showers produced once a track ends -> decay
    // 2) showers produced mid-way through a track (Brem, etc...)

    // keep track of the smallest distance from the shower start point
    // to the possible shower source on the track
    double distMin = std::numeric_limits<double>::max();

    // Case 1)
    // Check distance from shower start and track end
    // Do not care about relative directions:
    // generally at the track end energies are low and it is easy
    // to produce decay electrons with a very different direction
    // from the track's (also, the neutrino takes momentum)
    double distTrkEnd = shr.Start().Dist(trk.back());
    if (_debug) { std::cout << "Distance from shr start to trk end: " << distTrkEnd << std::endl; }
    if ( distTrkEnd < distMin ) { distMin = distTrkEnd; }
    
    // Case 2)
    // Need to find if shower starts from the trunk of the track
    // not close to the start point (in which case this could be
    // a neutrino event which produces a track and a shower)
    // To do this find the Impact Param of the shower projected
    // backwards with the track. If this is small and far enough
    // away from the start point -> use this distance
    geoalgo::Point_t s_pt(3);
    geoalgo::Point_t t_pt(3);
    double distTrk = sqrt( _geoAlgo.SqDist( shr, trk, s_pt, t_pt) );
    double IP_to_Trk = trk.front().Dist(t_pt); // distance from Track Start to IP point on track
    double IP_to_Shr = shr.Start().Dist(s_pt); // distance from Shower Start to IP point on shower
    // Before deciding 
    // Require that the closest approach point is > 10 cm away from the track start point
    
    if (_debug) {
      std::cout << "Impact Param between Shr Backwards & Trk: " << distTrk << std::endl;
      std::cout << "IP dist to Shower: " << IP_to_Trk << std::endl;
      std::cout << "IP dist to Track:  " << IP_to_Shr << std::endl;
    }
    
    return distMin;
  }


  double AlgoLonelyE::isShowerFromShower(const geoalgo::HalfLine_t& islonely, 
					 const geoalgo::HalfLine_t& isparent) const
  {

    // Try and determine if the shower under examination ("islonely")
    // originated from the "isparent" shower
    // Do this by checking for directionality agreement
    // and finding the distance between the two objects

    // keep track of the smallest distance from the shower start point
    // to the possible shower source on the other shower
    double distMin = std::numeric_limits<double>::max();

    // Trace back the directions of the two showers and find Impact Parameter
    // Then see how far this is from the two shower start points
    // require it to be before the "islonely" shower and after the 
    // "isparent" shower.
    // if before both, it could be that this is a Pi0 from a nu-event
    // so we don't want to remove that
    
    // keep track of IP points on "islonely" and "isparent" showers
    geoalgo::Point_t pt_a(3);
    geoalgo::Point_t pt_b(3);
    double distShr = sqrt( _geoAlgo.SqDist(islonely, isparent, pt_a, pt_b) );
    if (distShr < distMin) { distMin = distShr; }
    if (_debug) {
      std::cout << "Impact Parameter for Backwards Showers: " << distShr << std::endl;
      std::cout << "IP dist to shower : " << pt_a.Dist(islonely.Start()) << std::endl;
      std::cout << "IP dist to parent : " << pt_b.Dist(isparent.Start()) << std::endl;
    }

    return distMin;
  }

}

#endif