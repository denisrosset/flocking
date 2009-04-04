#include <cmath>
#include "flock.h"
#include "force.h"
#include "noise.h"
#include "neighbor.h"
#include "velocity.h"
#include "algorithm.h"

template<class NeighborSelector,
  class VelocityUpdater,
  class PositionAlgorithm,
  class ForceEvaluator0,
  class ForceEvaluator1,
  class ForceEvaluator2,
  class ForceEvaluator3>
  class FlockStep
{
 public:
 FlockStep(double dt,
	   NeighborSelector neighborSelector,
	   VelocityUpdater velocityUpdater,
	   PositionAlgorithm positionAlgorithm,
	   ForceEvaluator0 forceEvaluator0,
	   ForceEvaluator1 forceEvaluator1,
	   ForceEvaluator2 forceEvaluator2,
	   ForceEvaluator3 forceEvaluator3)
   :dt_(dt),
    neighborSelector_(neighborSelector),
    velocityUpdater_(velocityUpdater),
    positionAlgorithm_(positionAlgorithm),
    forceEvaluator0_(forceEvaluator0),
    forceEvaluator1_(forceEvaluator1),
    forceEvaluator2_(forceEvaluator2),
    forceEvaluator3_(forceEvaluator3)
    {
    }
  
  void step(Flock & flock) 
  {
    neighborSelector_.update(flock,
			     forceEvaluator0_,
			     forceEvaluator1_,
			     forceEvaluator2_,
			     forceEvaluator3_);
    positionAlgorithm_.update(flock, velocityUpdater_, dt_);
  }
  
  double dt_;
  NeighborSelector neighborSelector_;
  VelocityUpdater velocityUpdater_;
  PositionAlgorithm positionAlgorithm_;
  ForceEvaluator0 forceEvaluator0_;
  ForceEvaluator1 forceEvaluator1_;
  ForceEvaluator2 forceEvaluator2_;
  ForceEvaluator3 forceEvaluator3_;
};
