#include <assert.h>
#include <algorithm>
#include <iostream>
#include <boost/math/distributions/normal.hpp>

#include "process.hh"
#include "mypoisson.hh"

using namespace boost::math;

Process::Process( const double maximum_rate, const double s_brownian_motion_rate, const double s_outage_escape_rate, const int bins )
  : _probability_mass_function( bins, maximum_rate, 0 ),
    _gaussian( maximum_rate, bins * 2 ),
    _brownian_motion_rate( s_brownian_motion_rate ),
    _outage_escape_rate( s_outage_escape_rate ),
    _normalized( false )
{
  normalize();
}

std::ostream& operator<<(std::ostream& os, const Process& process)
{
    process.pmf().for_each( [&] ( const double midpoint, const double & value, unsigned int index )
			   {
           os << "["<< index << "]" << "midpoint " << midpoint << ", value = " << value << std::endl;
			   } );

    return os;
}

void Process::observe( const double time, const int counts )
{
  _normalized = false;

  /* multiply by likelihood function */
  _probability_mass_function.for_each( [&]
				       ( const double midpoint, double & value, const unsigned int index )
				       {
					 value *= poissonpdf( midpoint * time, counts );
				       } );
}

void Process::normalize( void )
{
  if ( _normalized ) {
    return;
  }

  double sum( 0 );

  /* find the total */
  _probability_mass_function.for_each( [&sum]
				       ( const double, const double & value, const unsigned int index )
				       {
					 sum += value;
				       } );

  /* normalize */
  _probability_mass_function.for_each( [&sum]
				       ( const double, double & value, const unsigned int index )
				       {
					 value /= sum;
				       } );

  _normalized = true;
}

void Process::evolve( const double time )
{
  _normalized = false;

  /* initialize brownian motion */
  double stddev = _brownian_motion_rate * sqrt( time );
  _gaussian.calculate( stddev );

  /* initialize new pmf */
  SampledFunction new_pmf( _probability_mass_function );
  new_pmf.for_each( [] ( const double, double & value, const unsigned int index ) { value = 0; } );

  const double zero_escape_probability = 1 - poissonpdf( time * _outage_escape_rate, 0 );

#if DEBUG
  std::cout << "stddev = " << stddev << ", _outage_escape_rate = " << _outage_escape_rate 
    << ", zero_escape_probability = " << zero_escape_probability << std::endl;
#endif

  _probability_mass_function.for_each( [&]
				       ( const double old_rate, const double & old_prob, const unsigned int old_index )
				       {
					 new_pmf.for_range( old_rate - 5 * stddev,
							    old_rate + 5 * stddev,
							    [&]
							    ( const double new_rate, double & new_prob, const unsigned int new_index )
							    {
							      double zfactor = 1.0;
							      
							      if ( old_index == 0 ) {
								zfactor = ( new_index != 0 ) ? zero_escape_probability : (1 - zero_escape_probability);
							      }
							      
                    double cell_diff = new_pmf.sample_ceil( new_rate ) - old_rate;
                    double floor_diff = new_pmf.sample_floor( new_rate ) - old_rate;
                    double cell_cdf = _gaussian.cdf(cell_diff);
                    double floor_cdf = _gaussian.cdf(floor_diff);
                    double pdf =  cell_cdf - floor_cdf;
							      new_prob += zfactor * old_prob * pdf;
                    assert(cell_diff > floor_diff);

                    // std::cout << std::setprecision(2)<< "old_rate = " << old_rate << ", new_rate = " << new_rate
                    // << ", old_index = " << old_index << ", new_index = " << new_index
                    // << ", zfactor = " << zfactor
                    // << ", cell_diff = " << cell_diff << ", floor_diff = " << floor_diff
                    // << ", cell_cdf = " << cell_cdf << ", floor_cdf = " << floor_cdf << ", gaussian prob = " << pdf
                    // << ", old_prob = " << old_prob
                    // << ", new_prob = " << new_prob << std::endl;
							    } );
				       } );
  
  _probability_mass_function = new_pmf;
}

Process::GaussianCache::GaussianCache( const double maximum_rate, const int bins )
  : _cdf( bins, maximum_rate, -maximum_rate ),
    _stddev( -1 )
{}

void Process::GaussianCache::calculate( const double s_stddev )
{
  if ( s_stddev == _stddev ) {
    return;
  }

  _stddev = s_stddev;
  normal diffdist( 0, _stddev );

  _cdf.for_each( [&] ( const double x, double & value, const unsigned int index ) { value = boost::math::cdf( diffdist, x ); } );
}

void Process::set_certain( const double rate )
{
  _normalized = false;

  unsigned int index_to_hit = _probability_mass_function.index( rate );

  _probability_mass_function.for_each( [&] ( const double midpoint,
					     double & value,
					     const unsigned int index )
				       {
					 if ( index == index_to_hit ) {
					   value = 1.0;
					 } else {
					   value = 0.0;
					 }
				       } );

  normalize();

  assert( _probability_mass_function[ rate ] == 1.0 );
}

Process & Process::operator=( const Process & other )
{
  _probability_mass_function = other._probability_mass_function;
  _gaussian = other._gaussian;
  _normalized = other._normalized;
  *( const_cast< double * >( &_brownian_motion_rate ) ) = other._brownian_motion_rate;

  return *this;
}

double Process::count_probability( const double time, const int counts )
{
  double ret = 0.0;

  _probability_mass_function.for_each( [&] ( const double rate,
					     const double & rate_probability,
					     const unsigned int index )
				       {
					 ret += rate_probability * poissonpdf( rate * time, counts );

          //  std::cout << "rate_probability = " << rate_probability << ", p = " << poissonpdf( rate * time, counts )
          //     << ", rate = " << rate << ", time = " << time << ", counts = " << counts << ", ret = " << ret << std::endl;
				       } );

  return ret;
}
