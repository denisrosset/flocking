#ifndef _FORCE_H
#define _FORCE_H
#include "flock.h"
#include <cmath>
#include <algorithm>
class DummyForceEvaluator
{
 public:
  void start(Flock & flock, int i, vector & temp)
  {
  }
  void update(Flock & flock, int i, int j, const vector & r, 
	      double normr, double normrsq, vector & temp, int Nn)
  {
  }
  void end(Flock & flock, int i, vector & temp, int Nn)
  {
  }
};

class OriginalVicsekAverageForceEvaluator
{
 public:
  void start(Flock & flock, int i, vector & temp)
  {
    temp[0] = temp[1] = 0;
  }
  void update(Flock & flock, int i, int j, const vector & r,
	      double normr, double normrsq, vector & temp, int Nn)
  {
    temp[0] += flock.v_[j][0];
    temp[1] += flock.v_[j][1];
  }
  void end(Flock & flock, int i, vector & temp, int Nn)
  {
    flock.f_[i][0] = (temp[0] + flock.v_[i][0]) / (Nn + 1);
    flock.f_[i][1] = (temp[1] + flock.v_[i][1]) / (Nn + 1);
  }
};

class VicsekAverageForceEvaluator
{
 public:
 VicsekAverageForceEvaluator(double beta) : beta_(beta)
  {
  }
  void start(Flock & flock, int i, vector & temp)
  {
    temp[0] = temp[1] = 0;
  }
  void update(Flock & flock, int i, int j, const vector & r,
	      double normr, double normrsq, vector & temp, int Nn)
  {
    temp[0] += flock.v_[j][0];
    temp[1] += flock.v_[j][1];
  }
  void end(Flock & flock, int i, vector & temp, int Nn)
  {
    vector veff;
    veff[0] = (temp[0] + flock.v_[i][0]) / (Nn + 1);
    veff[1] = (temp[1] + flock.v_[i][1]) / (Nn + 1);
    flock.f_[i][0] += (veff[0] - flock.v_[i][0]) * beta_;
    flock.f_[i][1] += (veff[1] - flock.v_[i][1]) * beta_;
  }
  double beta_;
};

class NeighborAverageForceEvaluator
{
 public:
 NeighborAverageForceEvaluator(double beta) : beta_(beta)
  { }
  void start(Flock & flock, int i, vector & temp)
  {
    temp[0] = temp[1] = 0;
  }
  void update(Flock & flock, int i, int j, const vector & r,
	      double normr, double normrsq, vector & temp, int Nn)
  {
    temp[0] += flock.v_[j][0] - flock.v_[i][0];
    temp[1] += flock.v_[j][1] - flock.v_[i][1];
  }
  void end(Flock & flock, int i, vector & temp, int Nn)
  {
    flock.f_[i][0] += beta_ * temp[0];
    flock.f_[i][1] += beta_ * temp[1];
  }
  double beta_;
};

class CruisingRegulatorForceEvaluator
{
 public:
 CruisingRegulatorForceEvaluator(double gamma, double v) :
  gamma_(gamma), v_(v)
  {
  }
  void start(Flock & flock, int i, vector & temp)
  {
  }
  void update(Flock & flock, int i, int j, const vector & r,
	      double normr, double normrsq, vector & temp, int Nn)
  {
  }
  void end(Flock & flock, int i, vector & temp, int Nn)
  {
    double vnorm = sqrt(flock.v_[i][0] * flock.v_[i][0]
			+ flock.v_[i][1] * flock.v_[i][1]);
    double factor = gamma_ * (v_ - vnorm) / vnorm;
    flock.f_[i][0] += flock.v_[i][0] * factor;
    flock.f_[i][1] += flock.v_[i][1] * factor;
  }
  double gamma_;
  double v_;
};

class LennardJonesInteractionForceEvaluator
{
 public:
  LennardJonesInteractionForceEvaluator(double epsilon, double sigma,
					double offset) :
  epsilon_(epsilon), sigma_(sigma), offset_(offset)
  { 
  }
  void start(Flock & flock, int i, vector & temp)
  {
    temp[0] = temp[1] = 0;
  }
  void update(Flock & flock, int i, int j, const vector & r,
	      double normr, double normrsq, vector & temp, int Nn)
  {
    double sigma_over_d_2 = sigma_ * sigma_ / normrsq;
    double sigma_over_d_4 = sigma_over_d_2 * sigma_over_d_2;
    double sigma_over_d_6 = sigma_over_d_2 * sigma_over_d_4;
    double sigma_over_d_12 = sigma_over_d_6 * sigma_over_d_6;
    double interaction_force = 4 * epsilon_ * 
      (sigma_over_d_12 - sigma_over_d_6) + offset_;
    temp[0] += interaction_force * r[0] / normr;
    temp[1] += interaction_force * r[1] / normr;
  }
  void end(Flock & flock, int i, vector & temp, int Nn)
  {
    flock.f_[i][0] += temp[0];
    flock.f_[i][1] += temp[1];
  }
  double epsilon_;
  double sigma_;
  double offset_;
};

class PiecewiseLinearForceEvaluator
{
 public:
 PiecewiseLinearForceEvaluator(double Frep, double Fattr, double r0, double r1)
   : Frep_(Frep), Fattr_(Fattr), r0_(r0), r1_(r1)
  {
  }
  void start(Flock & flock, int i, vector & temp)
  {
    temp[0] = temp[1] = 0;
  }
  void update(Flock & flock, int i, int j, const vector & r,
	      double normr, double normrsq, vector & temp, int Nn)
  {
    double where = std::max(r0_, normr);
    where = std::min(r1_, normr);
    double interaction_force = Frep_ + (Fattr_ - Frep_) * (where - r0_)
      / (r1_ - r0_);
    temp[0] += interaction_force * r[0] / normr;
    temp[1] += interaction_force * r[1] / normr;
  }
  void end(Flock & flock, int i, vector & temp, int Nn)
  {
    flock.f_[i][0] += temp[0];
    flock.f_[i][1] += temp[1];
  }
  double Frep_;
  double Fattr_;
  double r0_;
  double r1_;
};

#endif // _FORCE_H
