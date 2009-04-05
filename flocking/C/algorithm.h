#ifndef _ALGORITHM_H
#define _ALGORITHM_H

class OriginalVicsekAlgorithm
{
 public:
  template<class VelocityUpdater>
    void update(Flock & flock,
		VelocityUpdater & velocity_updater,
		double dt)
    {
#pragma omp parallel for schedule(static)
      for (int i = 0; i < flock.N_; i ++) {
	flock.x_[i][0] = flock.getCoordinateInOriginalDomain
	  (flock.x_[i][0] + flock.v_[i][0] * dt);
	flock.x_[i][1] = flock.getCoordinateInOriginalDomain
	  (flock.x_[i][1] + flock.v_[i][1] * dt);
	velocity_updater.update(flock, i, dt);
      }
    }
};

class StandardVicsekAlgorithm
{
 public:
  template<class VelocityUpdater>
    void update(Flock & flock,
		VelocityUpdater & velocity_updater,
		double dt)
    {
#pragma omp parallel for schedule(static)
      for (int i = 0; i < flock.N_; i ++) {
	velocity_updater.update(flock, i, dt);
	flock.x_[i][0] = flock.getCoordinateInOriginalDomain
	  (flock.x_[i][0] + flock.v_[i][0] * dt);
	flock.x_[i][1] = flock.getCoordinateInOriginalDomain
	  (flock.x_[i][1] + flock.v_[i][1] * dt);
      }
    }
};

#endif // _ALGORITHM_H
