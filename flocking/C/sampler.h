#ifndef _MEASURE_H
#define _MEASURE_H
#include "flock.h"
#include "force.h"
#include "neighbor.h"
#include <bitset>
#include <vector>
#include <cmath>
#include <algorithm>
#include <string>
#include <numeric>

template<int N>
class CompactAdjacencyMatrixBitSetter
{
 public:
 CompactAdjacencyMatrixBitSetter(std::bitset<N * N> & bitset) : bitset_(bitset) { }
  void start(Flock & flock, int i, vector & temp) { }
  void update(Flock & flock, int i, int j, const vector & r,
	      double normr, double normrsq, vector & temp, int Nn)
  {
    // we have j \in N_{i}
    bitset_.set(N * i + j);
  }
  void end(Flock & flock, int i, vector & temp, int Nn) { }
  std::bitset<N * N> & bitset_;
};

template<int N>
class CompactAdjacencyMatrix
{
 public:
  template<class NeighborSelector>
    std::string compute(Flock & flock, NeighborSelector neighborSelector)
    {
      std::bitset<N * N> bitset;
      neighborSelector.update(flock, 
			      CompactAdjacencyMatrixBitSetter<N>(bitset),
			      DummyForceEvaluator(),
			      DummyForceEvaluator(),
			      DummyForceEvaluator());
      return bitset.to_string();
    }
};

// inefficient N**3 algorithm
template<int N>
class UnnormalizedClusterSizeDistribution
{
 public:
  template<class NeighborSelector>
    void compute(Flock & flock,
		 NeighborSelector neighborSelector,
		 int * distribution)
    {
      std::bitset<N * N> bitset;
      neighborSelector.update(flock, 
			      CompactAdjacencyMatrixBitSetter<N>(bitset),
			      DummyForceEvaluator(),
			      DummyForceEvaluator(),
			      DummyForceEvaluator());
      std::vector<int> color(N);
      std::vector<int> size(N);
      for (int i = 0; i < N; i ++) {
	color[i] = i + 1;
	for (int j = i + 1; j < N; j ++) {
	  bool connected = bitset.test(i * N + j) && bitset.test(j * N + i);
	  if (connected) {
	    if (color[j] != 0)
	      for (int k = 0; k < N; k ++)
		if (j != k && color[k] == color[j])
		  color[k] = color[i];
	    color[j] = color[i];
	  }
	}
      }
      for (int i = 0; i < N; i ++) {
	for (int j = 0; j < N; j ++) {
	  if (color[j] == i)
	    size[i] ++;
	}
      }
      for (int i = 0; i < N; i ++)
	distribution[size[color[i]]] ++;
    }
};

typedef int edge[2];
class EdgeAdder
{
 public:
 EdgeAdder(edge ** edgeptr)
   : edgeptr_(edgeptr) { }
  void start(Flock & flock, int i, vector & temp) { }
  void update(Flock & flock, int i, int j, const vector & r,
	      double normr, double normrsq, vector & temp, int Nn)
  {
    **edgeptr_[0] = i;
    **edgeptr_[1] = j;
    (*edgeptr_) ++;
  }
  void end(Flock & flock, int i, vector & temp, int Nn) { }
  edge ** edgeptr_;
};

class ListOfEdges
{
 public:
  template<class NeighborSelector>
    int compute(Flock & flock, NeighborSelector neighborSelector, edge * edgelist)
    {
      edge * edgeptr = edgelist;
      neighborSelector.update(flock, 
			      EdgeAdder(&edgeptr),
			      DummyForceEvaluator(),
			      DummyForceEvaluator(),
			      DummyForceEvaluator());
      return edgeptr - edgelist;
    }
};

class NearestNeighborDistance
{
 public:
 NearestNeighborDistance(std::vector<double> & vector__)
   : vector_(vector__)
  { }
  void start(Flock & flock, int i, vector & temp)
  {
    temp[0] = flock.L_ * flock.L_ * 2;
  }
  void update(Flock & flock, int i, int j, const vector & r,
	      double normr, double normrsq, vector & temp, int Nn)
  {
    if (normrsq < temp[0])
      temp[0] = normrsq;
  }
  void end(Flock & flock, int i, vector & temp, int Nn)
  {
    if (temp[0] < flock.L_ * flock.L_ * 2)
      vector_.push_back(std::sqrt(temp[0]));
  }
  std::vector<double> & vector_;
};

class MinNearestNeighborDistance
{
 public:
  template<class NeighborSelector>
    double compute(Flock & flock, NeighborSelector neighborSelector)
    {
      std::vector<double> vector;
      neighborSelector.update(flock, 
			      NearestNeighborDistance(vector),
			      DummyForceEvaluator(),
			      DummyForceEvaluator(),
			      DummyForceEvaluator());
      if (vector.size() > 0)
	return *std::min_element(vector.begin(), vector.end());
      else
	return -1;
    }
};

class MaxNearestNeighborDistance
{
 public:
  template<class NeighborSelector>
    double compute(Flock & flock, NeighborSelector neighborSelector)
    {
      std::vector<double> vector;
      neighborSelector.update(flock, 
			      NearestNeighborDistance(vector),
			      DummyForceEvaluator(),
			      DummyForceEvaluator(),
			      DummyForceEvaluator());
      if (vector.size() > 0)
	return *std::max_element(vector.begin(), vector.end());
      else
	return -1;
    }
};

class MeanNearestNeighborDistance
{
 public:
  template<class NeighborSelector>
    double compute(Flock & flock, NeighborSelector neighborSelector)
    {
      std::vector<double> vector;
      neighborSelector.update(flock, 
			      NearestNeighborDistance(vector),
			      DummyForceEvaluator(),
			      DummyForceEvaluator(),
			      DummyForceEvaluator());
      if (vector.size() > 0)
	return std::accumulate(vector.begin(), vector.end(), 0.0) / vector.size();
      else
	return -1;
    }
};

#endif // _MEASURE_H
