#ifndef _NEIGHBOR_H
#define _NEIGHBOR_H
#include "hashingneighbors/PointSet.h"
#include "blockneighbors/BlockPointSet.h"
#include <cmath>
class TopologicalDistanceNeighborSelector
{
 public:
 TopologicalDistanceNeighborSelector(int k)
   : k_(k)
  {
  }
  
  template<
    class ForceEvaluator0,
    class ForceEvaluator1,
    class ForceEvaluator2,
    class ForceEvaluator3
    >
    void update(Flock & flock,
		ForceEvaluator0 forceEvaluator0,
		ForceEvaluator1 forceEvaluator1,
		ForceEvaluator2 forceEvaluator2,
		ForceEvaluator3 forceEvaluator3)
    {
      int m = k_ + 2;
      int r = 10;
      PointSet<2> pointset(flock.x_, flock.N_, m, r);
      pointset.init();
#pragma omp parallel for schedule(guided, 8)
      for(int i = 0; i < flock.N_; i ++) {
	vector temp[4];
	int Nn = 0;
	forceEvaluator0.start(flock, i, temp[0]);
	forceEvaluator1.start(flock, i, temp[1]);
	forceEvaluator2.start(flock, i, temp[2]);
	forceEvaluator3.start(flock, i, temp[3]);
	NeighborList * neighborlist = pointset.getWrapNeighborListInRealOrder
	  (flock.x_[i], k_ + 1, flock.L_);
	neighborlist->sortFinalResults();
	NeighborList::const_iterator it = neighborlist->begin();
	++it; // first element is myself
	for(; it != neighborlist->end(); ++it) {
	  int j = it->second;
	  vector r;
	  // TODO : replace normrsq by it->first
	  r[0] = flock.getCoordinateDifference(flock.x_[i][0], flock.x_[j][0]);
	  r[1] = flock.getCoordinateDifference(flock.x_[i][1], flock.x_[j][1]);
	  double normrsq = r[0]*r[0] + r[1]*r[1];
	  double normr = std::sqrt(normrsq);
	  forceEvaluator0.update(flock, i, j, r, normr, normrsq, temp[0], Nn);
	  forceEvaluator1.update(flock, i, j, r, normr, normrsq, temp[1], Nn);
	  forceEvaluator2.update(flock, i, j, r, normr, normrsq, temp[2], Nn);
	  forceEvaluator3.update(flock, i, j, r, normr, normrsq, temp[3], Nn);
	  Nn ++;
	}
	forceEvaluator0.end(flock, i, temp[0], Nn);
	forceEvaluator1.end(flock, i, temp[1], Nn);
	forceEvaluator2.end(flock, i, temp[2], Nn);
	forceEvaluator3.end(flock, i, temp[3], Nn);
	delete neighborlist;
      }
    }
  int k_;
};

class TopologicalDistanceCutoffNeighborSelector
{
 public:
 TopologicalDistanceCutoffNeighborSelector(int k, double R)
   : k_(k), R_(R)
  {
  }

  template<
    class ForceEvaluator0,
    class ForceEvaluator1,
    class ForceEvaluator2,
    class ForceEvaluator3
    >
    void update(Flock & flock,
		ForceEvaluator0 forceEvaluator0,
		ForceEvaluator1 forceEvaluator1,
		ForceEvaluator2 forceEvaluator2,
		ForceEvaluator3 forceEvaluator3)
    {
      int m = k_ + 2;
      int r = 10;
      PointSet<2> pointset(flock.x_, flock.N_, m, 10);
      pointset.init();
#pragma omp parallel for schedule(guided, 8)
      for(int i = 0; i < flock.N_; i ++) {
	vector temp[4];
	int Nn = 0;
	forceEvaluator0.start(flock, i, temp[0]);
	forceEvaluator1.start(flock, i, temp[1]);
	forceEvaluator2.start(flock, i, temp[2]);
	forceEvaluator3.start(flock, i, temp[3]);
	NeighborList * neighborlist = pointset.getWrapNeighborListInRealOrder
	  (flock.x_[i], k_ + 1, flock.L_);
	neighborlist->sortFinalResults();
	NeighborList::const_iterator it = neighborlist->begin();
	++it; // first element is myself
	for(; it != neighborlist->end(); ++it) {
	  int j = it->second;
	  vector r;
	  // TODO : replace normrsq by it->first
	  r[0] = flock.getCoordinateDifference(flock.x_[i][0], flock.x_[j][0]);
	  r[1] = flock.getCoordinateDifference(flock.x_[i][1], flock.x_[j][1]);
	  double normrsq = r[0]*r[0] + r[1]*r[1];
	  double normr = std::sqrt(normrsq);
	  if (normrsq <= R_ * R_) {
	    forceEvaluator0.update(flock, i, j, r, normr, normrsq, temp[0], Nn);
	    forceEvaluator1.update(flock, i, j, r, normr, normrsq, temp[1], Nn);
	    forceEvaluator2.update(flock, i, j, r, normr, normrsq, temp[2], Nn);
	    forceEvaluator3.update(flock, i, j, r, normr, normrsq, temp[3], Nn);
	  }
	}
	forceEvaluator0.end(flock, i, temp[0], Nn);
	forceEvaluator1.end(flock, i, temp[1], Nn);
	forceEvaluator2.end(flock, i, temp[2], Nn);
	forceEvaluator3.end(flock, i, temp[3], Nn);
	delete neighborlist;
      }
    }
  int k_;
  double R_;
};

class MetricDistanceNeighborSelector
{
 public:
 MetricDistanceNeighborSelector(double R) :
  R_(R)
  {
  }

  template<
    class ForceEvaluator0,
    class ForceEvaluator1,
    class ForceEvaluator2,
    class ForceEvaluator3
    >
    void update(Flock & flock,
		ForceEvaluator0 forceEvaluator0,
		ForceEvaluator1 forceEvaluator1,
		ForceEvaluator2 forceEvaluator2,
		ForceEvaluator3 forceEvaluator3)
    {
      BlockPointSet<2> pointset(flock.x_, flock.N_, R_, flock.L_);
#pragma omp parallel for schedule(guided, 8)
      for(int i = 0; i < flock.N_; i ++) {
	vector temp[4];
	int Nn = 0;
	forceEvaluator0.start(flock, i, temp[0]);
	forceEvaluator1.start(flock, i, temp[1]);
	forceEvaluator2.start(flock, i, temp[2]);
	forceEvaluator3.start(flock, i, temp[3]);
	int b_i[2], b[2];
	pointset.getBlockIndex(flock.x_[i], b_i);
	for (b[0] = b_i[0] - 1; b[0] < b_i[0] + 2; b[0] ++) {
	  for (b[1] = b_i[1] - 1; b[1] < b_i[1] + 2; b[1] ++) {
	    BlockPointSet<2>::BlockList * blocklist = pointset.get(b);
	    BlockPointSet<2>::BlockList::const_iterator it = blocklist->begin();
	    for (; it != blocklist->end(); ++it) {
	      int j = *it;
	      if (j != i) {
		vector r;
		r[0] = flock.getCoordinateDifference(flock.x_[i][0], flock.x_[j][0]);
		r[1] = flock.getCoordinateDifference(flock.x_[i][1], flock.x_[j][1]);
		double normrsq = r[0]*r[0] + r[1]*r[1];
		if (normrsq <= R_ * R_) {
		  double normr = std::sqrt(normrsq);
		  forceEvaluator0.update(flock, i, j, r, normr, normrsq, temp[0], Nn);
		  forceEvaluator1.update(flock, i, j, r, normr, normrsq, temp[1], Nn);
		  forceEvaluator2.update(flock, i, j, r, normr, normrsq, temp[2], Nn);
		  forceEvaluator3.update(flock, i, j, r, normr, normrsq, temp[3], Nn);
		}
	      }
	    }
	  }
	}
	forceEvaluator0.end(flock, i, temp[0], Nn);
	forceEvaluator1.end(flock, i, temp[1], Nn);
	forceEvaluator2.end(flock, i, temp[2], Nn);
	forceEvaluator3.end(flock, i, temp[3], Nn);
      }
    }
  double R_;
};

class BlockMetricDistanceNeighborSelector
{
 public:
 BlockMetricDistanceNeighborSelector(double R) :
  R_(R)
  {
  }

  template<
    class ForceEvaluator0,
    class ForceEvaluator1,
    class ForceEvaluator2,
    class ForceEvaluator3
    >
    void update(Flock & flock,
		ForceEvaluator0 forceEvaluator0,
		ForceEvaluator1 forceEvaluator1,
		ForceEvaluator2 forceEvaluator2,
		ForceEvaluator3 forceEvaluator3)
    {
      BlockPointSet<2> pointset(flock.x_, flock.N_, R_, flock.L_);
#pragma omp parallel for schedule(guided, 8)
      for(int i = 0; i < flock.N_; i ++) {
	vector temp[4];
	int Nn = 0;
	forceEvaluator0.start(flock, i, temp[0]);
	forceEvaluator1.start(flock, i, temp[1]);
	forceEvaluator2.start(flock, i, temp[2]);
	forceEvaluator3.start(flock, i, temp[3]);
	int b_i[2], b[2];
	pointset.getBlockIndex(flock.x_[i], b_i);
	for (b[0] = b_i[0] - 1; b[0] < b_i[0] + 2; b[0] ++) {
	  for (b[1] = b_i[1] - 1; b[1] < b_i[1] + 2; b[1] ++) {
	    BlockPointSet<2>::BlockList * blocklist = pointset.get(b);
	    BlockPointSet<2>::BlockList::const_iterator it = blocklist->begin();
	    for (; it != blocklist->end(); ++it) {
	      int j = *it;
	      if (j != i) {
		vector r;
		r[0] = flock.getCoordinateDifference(flock.x_[i][0], flock.x_[j][0]);
		r[1] = flock.getCoordinateDifference(flock.x_[i][1], flock.x_[j][1]);
		double normrsq = r[0]*r[0] + r[1]*r[1];
		double normr = std::sqrt(normrsq);
		forceEvaluator0.update(flock, i, j, r, normr, normrsq, temp[0], Nn);
		forceEvaluator1.update(flock, i, j, r, normr, normrsq, temp[1], Nn);
		forceEvaluator2.update(flock, i, j, r, normr, normrsq, temp[2], Nn);
		forceEvaluator3.update(flock, i, j, r, normr, normrsq, temp[3], Nn);
	      }
	    }
	  }
	}
	forceEvaluator0.end(flock, i, temp[0], Nn);
	forceEvaluator1.end(flock, i, temp[1], Nn);
	forceEvaluator2.end(flock, i, temp[2], Nn);
	forceEvaluator3.end(flock, i, temp[3], Nn);
      }
    }
  double R_;
};

#endif // _NEIGHBOR_H
