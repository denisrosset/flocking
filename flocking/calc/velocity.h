#ifndef _VELOCITY_H
#define _VELOCITY_H

#include <cmath>

template<class NoiseAdder>
class OriginalVicsekVelocityUpdater
{
 public:
  OriginalVicsekVelocityUpdater(NoiseAdder noiseAdder, double v) 
    : noiseAdder_(noiseAdder), v_(v)
  {
  }
  void update(Flock & flock, int i, double dt)
  {
    vector newv;
    newv[0] = flock.f_[i][0];
    newv[1] = flock.f_[i][1];
    noiseAdder_.update(newv, flock.rnd_[i]);
    double factor = v_/std::sqrt(newv[0]*newv[0] + newv[1]*newv[1]);
    flock.v_[i][0] = newv[0] * factor;
    flock.v_[i][1] = newv[1] * factor;
  }
  NoiseAdder noiseAdder_;
  double v_;
};

#endif // _VELOCITY_H

/*
void constant_velocity_update(int i, vector & newv, double vv, double amax, double dt)
{
  newv[0] = v[i][0] + f[i][0] * dt;
  newv[1] = v[i][1] + f[i][1] * dt;
  double normnewv = sqrt(newv[0]*newv[0] + newv[1]*newv[1]);
  newv[0] /= normnewv * vv;
  newv[1] /= normnewv * vv;
  vector diff;
  diff[0] = newv[0] - v[i][0];
  diff[1] = newv[1] - v[i][1];
  double normdiffsq = diff[0]*diff[0] + diff[1]*diff[1];
  if (normdiffsq > vv * vv * amax * amax) {
    double factor = vv * amax / sqrt(normdiffsq);
    diff[0] *= factor;
    diff[1] *= factor;
    newv[0] = v[i][0] + diff[0];
    newv[1] = v[i][1] + diff[1];
  }
}

void variable_vmax_velocity_update(int i, vector & newv, double vmax, double amax, double dt)
{
  double normvsq = v[i][0] * v[i][0] + v[i][1] * v[i][1];
  newv[0] = v[i][0] + f[i][0] * dt;
  newv[1] = v[i][1] + f[i][1] * dt;
  double normnewvsq = newv[0] * newv[0] + newv[1] * newv[1];
  if (normnewvsq > vmax * vmax) {
    double normnewv = sqrt(normnewvsq);
    newv[0] *= vmax / normnewv;
    newv[1] *= vmax / normnewv;
  }
  vector diff;
  diff[0] = newv[0] - v[i][0];
  diff[1] = newv[1] - v[i][1];
  double normdiffsq = diff[0]*diff[0] + diff[1]*diff[1];
  if (normdiffsq > normvsq * amax * amax) {
    double factor = amax * sqrt(normvsq / normdiffsq);
    diff[0] *= factor;
    diff[1] *= factor;
    newv[0] = v[i][0] + diff[0];
    newv[1] = v[i][1] + diff[1];
  }
}


void variable_vmax_velocity_update(int i, vector & newv, double vmin, double vmax, double amax, double dt)
{
  double normvsq = v[i][0] * v[i][0] + v[i][1] * v[i][1];
  newv[0] = v[i][0] + f[i][0] * dt;
  newv[1] = v[i][1] + f[i][1] * dt;
  double normnewvsq = newv[0] * newv[0] + newv[1] * newv[1];
  if (normnewvsq > vmax * vmax) {
    double normnewv = sqrt(normnewvsq);
    newv[0] *= vmax / normnewv;
    newv[1] *= vmax / normnewv;
  } else if (normnewvsq < vmin * vmin) {
    double normnewv = sqrt(normnewvsq);
    newv[0] *= vmin / normnewv;
    newv[1] *= vmin / normnewv;
  }

  vector diff;
  diff[0] = newv[0] - v[i][0];
  diff[1] = newv[1] - v[i][1];
  double normdiffsq = diff[0]*diff[0] + diff[1]*diff[1];
  if (normdiffsq > normvsq * amax * amax) {
    double factor = amax * sqrt(normvsq / normdiffsq);
    diff[0] *= factor;
    diff[1] *= factor;
    newv[0] = v[i][0] + diff[0];
    newv[1] = v[i][1] + diff[1];
  }
}
*/
