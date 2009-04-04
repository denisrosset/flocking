#ifndef _FLOCK_H
#define _FLOCK_H

typedef double vector[2];

class Flock
{
 public:
 Flock(vector * x, vector * v, vector * f, double * rnd, int N, double L) : 
  x_(x), v_(v), f_(f), rnd_(rnd), N_(N), L_(L)
    {
    }
  double getCoordinateInOriginalDomain(double a)
  {
    a = a < 0 ? a + L_ : a;
    a = a > L_ ? a - L_ : a;
    return a;
  }
  double getCoordinateDifference(double a, double b)
  {
    double d = a - b;
    d = d < -L_/2 ? d + L_ : d;
    d = d > L_/2 ? d - L_ : d;
    return d;
  }
  double distanceBetweenBirdsSquared(int i, int j)
{
  double dx = getCoordinateDifference(x_[i][0], x_[j][0]);
  double dy = getCoordinateDifference(x_[i][1], x_[j][1]);
  return dx * dx + dy * dy;
}
  double distanceBetweenBirds(int i, int j)
  {
    return sqrt(distanceBetweenBirdsSquared(i, j));

  }
  vector * __restrict__ x_;
  vector * __restrict__ v_;
  vector * __restrict__ f_;
  double * __restrict__ rnd_;
  int N_;
  double L_;
};

#endif // _FLOCK_H
