#ifndef _FORCE_H
#define _FORCE_H

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

#endif // _FORCE_H

/*
void vicsek_average_force_add_term(int i, vector & force)
{
  force[0] += v[i][0];
  force[1] += v[i][1];
}

void vicsek_average_force_shape_term(int i, vector & force, double beta, int Nn)
{
  vector veff;
  veff[0] = (force[0] + v[i][0]) / (Nn + 1);
  veff[1] = (force[1] + v[i][1]) / (Nn + 1);
  force[0] = (veff[0] - v[i][0]) * beta;
  force[1] = (veff[1] - v[i][1]) * beta;
}

void neighbor_average_force_add_term(int self, int neighbor, vector & force)
{
  force[0] = v[neighbor][0] - v[self][0];
  force[1] = v[neighbor][1] - v[self][1];
}

void neighbor_average_force_shape_term(vector & force, double beta)
{
  force[0] *= beta;
  force[1] *= beta;
}

void cruising_regulator_force_shape_term(int i, vector & force, double gamma, double vv)
{
  double vnorm = sqrt(v[i][0]*v[i][0] + v[i][1]*v[i][1]);
  double factor = gamma * (vv - vnorm) / vnorm;
  force[0] = v[i][0] * factor;
  force[1] = v[i][1] * factor;
}

void lennard_jones_interaction_force_add_term(vector & force,
					      vector & r,
					      double normr,
					      double normrsq,
					      double epsilon,
					      double sigma,
					      double offset) {
  double sigma_over_d_2 = sigma*sigma/normrsq;
  double sigma_over_d_4 = sigma_over_d_2 * sigma_over_d_2;
  double sigma_over_d_6 = sigma_over_d_4 * sigma_over_d_2;
  double sigma_over_d_12 = sigma_over_d_6 * sigma_over_d_6;
  double interaction_force = 4 * epsilon * (sigma_over_d_12 - sigma_over_d_6) + offset;
  force[0] += interaction_force * r[0] / normr;
  force[1] += interaction_force * r[1] / normr;
}
void piecewise_linear_interaction_force_add_term(vector & force,
						 vector & r,
						 double normr,
						 double normrsq,
						 double Frep,
						 double Fattr,
						 double r0,
						 double r1) {
  double where = normr < r0 ? r0 : normr;
  where = normr > r1 ? r1 : normr;
  double interaction_force  = Frep + (Fattr - Frep) * (where - r0) / (r1 - r0);
  force[0] += interaction_force * r[0] / normr;
  force[1] += interaction_force * r[1] / normr;
}

*/
