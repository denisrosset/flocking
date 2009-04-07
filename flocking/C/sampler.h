#ifndef _MEASURE_H
#define _MEASURE_H
#include <vector>
#include <cmath>
#include <algorithm>
#include <string>
#include <numeric>
#include <boost/config.hpp>
#include <boost/graph/strong_components.hpp>
#include <boost/graph/adjacency_list.hpp>
#include "flock.h"
#include "force.h"
#include "neighbor.h"
#include <boost/graph/graph_traits.hpp>
//#include <boost/graph/dijkstra_shortest_paths.hpp>
//#include <boost/graph/graphviz.hpp>
#include <boost/graph/graph_utility.hpp>
//#include <utility>                   // for std::pair


class BitSet
{
 public:
 BitSet(unsigned char * repr) : repr_(repr) { }
  void set(int i)
  {
    repr_[i/8] ^= 1 << (i % 8);
  }
  unsigned char * repr_;
};
class CompactAdjacencyMatrixBitSetter
{
 public:
 CompactAdjacencyMatrixBitSetter(BitSet & bitset) : bitset_(bitset) { }
  void start(Flock & flock, int i, vector & temp) { }
  void update(Flock & flock, int i, int j, const vector & r,
	      double normr, double normrsq, vector & temp, int Nn)
  {
    // we have j \in N_{i}
    bitset_.set(flock.N_ * i + j);
  }
  void end(Flock & flock, int i, vector & temp, int Nn) { }
  BitSet & bitset_;
};


class CompactAdjacencyMatrix
{
 public:
  template<class NeighborSelector>
    void compute(Flock & flock, NeighborSelector neighborSelector, unsigned char * raw_set)
    {
      BitSet bitset(raw_set);
      neighborSelector.update(flock, 
			      CompactAdjacencyMatrixBitSetter(bitset),
			      DummyForceEvaluator(),
			      DummyForceEvaluator(),
			      DummyForceEvaluator());
    }
};

class GraphEdgeAdder
{
 public:
  typedef boost::adjacency_list<boost::vecS, boost::vecS, boost::bidirectionalS> Graph;
 GraphEdgeAdder(Graph & graph) : graph_(graph) { }
  void start(Flock & flock, int i, vector & temp) { }
  void update(Flock & flock, int i, int j, const vector & r,
	      double normr, double normrsq, vector & temp, int Nn)
  {
    boost::add_edge(i, j, graph_);
  }
  void end(Flock & flock, int i, vector & temp, int Nn) { }
  Graph & graph_;
};

class ColorComponents
{
 public:
  template<class NeighborSelector>
    void compute(Flock & flock,
		 NeighborSelector neighborSelector,
		 long * color)
    {
      typedef boost::graph_traits<GraphEdgeAdder::Graph>::vertex_descriptor Vertex;
      GraphEdgeAdder::Graph graph(flock.N_);
      std::vector<int> component(flock.N_), discover_time(flock.N_);
      std::vector<boost::default_color_type> color_vector(flock.N_);
      std::vector<Vertex> root(flock.N_);
      neighborSelector.update(flock,
			      GraphEdgeAdder(graph),
			      DummyForceEvaluator(),
			      DummyForceEvaluator(),
			      DummyForceEvaluator());
      boost::strong_components(graph, &component[0]/*, 
			       boost::root_map(&root[0]).
			       boost::color_map(&color_vector[0]).
			       boost::discover_time_map(&discover_time[0])*/);
      for (int i = 0; i != flock.N_; ++i)
	color[i] = component[i];
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
    (**edgeptr_)[0] = i;
    (**edgeptr_)[1] = j;
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
