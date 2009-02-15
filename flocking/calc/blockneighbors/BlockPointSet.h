#include <list>
#include <vector>
#include <cmath>
/** Represent a set of points, delimited in blocks. Wrap-around is
    implemented as a special case.

    Using M as a template parameter is an ugly hack to have constant
    compile-time array size for block
*/
template<int d>
class BlockPointSet
{
 public:
  typedef double Point[d];
  typedef std::list<int> BlockList;
  BlockList * get(int b[d])
  {
    int index = 0;
    for (int a = 0; a < d; a ++) {
      if (b[a] < 0 || b[a] >= M_ + 2)
	return NULL;
      index = index * (M_ + 2) + b[a];
    }
    return &block_[index];
  }
 BlockPointSet(const Point * x, int N, double R, double L)
   : x_(x), N_(N), R_(R), L_(L)
  {
    M_ = (int)std::ceil(L_ / R_);
    block_.resize(getBlockArraySize());
    addPoints();
  }
  void getBlockIndex(const Point& x, int index[d])
  {
    for (int a = 0; a < d; a ++)
      index[a] = int(x[a] / R_) + 1;
  }
 protected:
  int getBlockArraySize()
  {
    int size = 1;
    for (int a = 0; a < d; a ++)
      size *= M_ + 2;
    return size;
  }

  void addPoints()
  {
    for (int i = 0; i < N_; i ++) {
      int shift[d];
      for (int a = 0; a < d; a ++)
	shift[a] = -1;
      while (true) {
	int b[d];
	int a = 0;
	for (a = 0; a < d; a ++) {
	  b[a] = int((x_[i][a] + shift[a] * L_) / R_) + 1;
	  if (b[a] < 0 || b[a] >= M_ + 2)
	    break;
	}
	if (a == d)
	  get(b)->push_back(i);
	a = -1;
	do {
	  a ++;
	  if (a == d)
	    break;
	  shift[a] ++;
	  if (shift[a] == 2)
	    shift[a] = -1;
	} while (shift[a] == -1);
	if (a == d)
	  break;
      }
    }
  }
  const Point * x_;
  int N_;
  double R_;
  double L_;
  int M_;
  std::vector<std::list<int> > block_;
};
