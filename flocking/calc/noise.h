#ifndef _NOISE_H
#define _NOISE_H

class DummyNoiseAdder
{
 public:
  void update(vector & v, double rnd)
  {
  }
};

class ScalarNoiseAdder
{
 public:
  ScalarNoiseAdder(double eta) : eta_(eta)
  {
  }
  void update(vector & v, double rnd)
  {
    vector ov;
    ov[0] = v[0]; 
    ov[1] = v[1];
    double angle = (rnd - 0.5) * 2 * M_PI * eta_;
    double cs = cos(angle), sn = sin(angle);
    v[0] = cs * ov[0] - sn * ov[1];
    v[1] = sn * ov[0] + cs * ov[1];
  }
  double eta_;
};

class VectorialNoiseAdder
{
 public:
  VectorialNoiseAdder(double eta, double v)
    : eta_(eta), v_(v)
  {
  }
  void update(vector & v, double rnd)
  {
    double angle = (rnd - 0.5) * 2 * M_PI;
    v[0] = (1 - eta_) * v[0] + eta_ * v_ * cos(angle);
    v[1] = (1 - eta_) * v[1] + eta_ * v_ * sin(angle);
  }
  double eta_;
  double v_;
};
#endif // _NOISE_H
