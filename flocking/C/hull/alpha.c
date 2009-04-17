#include <float.h>
#include <math.h>
#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include <locale.h>
#include <string.h>
#include "getopt.h"
#include <ctype.h>

/*
 * Ken Clarkson wrote this.  Copyright (c) 1995 by AT&T..
 * Modified by Denis Rosset 2009 to output alpha shapes from stdin to stdout
 * Permission to use, copy, modify, and distribute this software for any
 * purpose without fee is hereby granted, provided that this entire notice
 * is included in all copies of any software which is or includes a copy
 * or modification of this software and in all copies of the supporting
 * documentation for such software.
 * THIS SOFTWARE IS BEING PROVIDED "AS IS", WITHOUT ANY EXPRESS OR IMPLIED
 * WARRANTY.  IN PARTICULAR, NEITHER THE AUTHORS NOR AT&T MAKE ANY
 * REPRESENTATION OR WARRANTY OF ANY KIND CONCERNING THE MERCHANTABILITY
 * OF THIS SOFTWARE OR ITS FITNESS FOR ANY PARTICULAR PURPOSE.
 */

#define POINTSITES 1

#include "hull.h"

point	site_blocks[MAXBLOCKS];
int	num_blocks;

/* int	getopt(int, char**, char*); */
extern char	*optarg;
extern int optind;
extern int opterr;

static long num_sites;
static short vd = 0;
static int dim;

FILE *INFILE, *OUTFILE, *DFILE;

static long site_numm(site p) {

	long i,j;

	if (vd && p==hull_infinity) return -1;
	if (!p) return -2;
	for (i=0; i<num_blocks; i++)
		if ((j=p-site_blocks[i])>=0 && j < BLOCKSIZE*dim) 
			return j/dim+BLOCKSIZE*i;
	return -3;
}


static site new_site (site p, long j) {

	assert(num_blocks+1<MAXBLOCKS);
	if (0==(j%BLOCKSIZE)) {
		assert(num_blocks < MAXBLOCKS);
		return(site_blocks[num_blocks++]=(site)malloc(BLOCKSIZE*site_size));
	} else
		return p+dim;
}

site read_next_site(long j){

	int i=0, k=0;
	static char buf[100], *s;

	if (j!=-1) p = new_site(p,j);
	if (j!=0) while ((s=fgets(buf,sizeof(buf),INFILE))) {
 		if (buf[0]=='%') continue;
		for (k=0; buf[k] && isspace(buf[k]); k++);
		if (buf[k]) break;
	}
	if (!s) return 0;
	while (buf[k]) {
		while (buf[k] && isspace(buf[k])) k++;
		if (buf[k] && j!=-1) {
			if (sscanf(buf+k,"%lf",p+i)==EOF) {
				fprintf(DFILE, "bad input line: %s\n", buf);
				exit(1);
			}
			p[i] = floor(mult_up*p[i]+0.5);   
			mins[i] = (mins[i]<p[i]) ? mins[i] : p[i];
			maxs[i] = (maxs[i]>p[i]) ? maxs[i] : p[i];
		}
		if (buf[k]) i++;
		while (buf[k] && !isspace(buf[k])) k++;
	}

	if (!dim) dim = i;
	if (i!=dim) {DEB(-10,inconsistent input);DEBTR(-10); exit(1);}	
	return p;
}




/*
site read_next_site(long j){

	int i;
	double pi;

	p = new_site(p,j);
	for (i=0; (i<dim) && (fscanf(INFILE,"%lf",p+i)!=EOF); i++) {
		pi = p[i] *= mult_up;
		p[i] = floor(p[i]+0.5);   
		if (abs(p[i]-pi)>1) {DEB(-3,uhoh);DEBTR(-3); exit(1);}
		mins[i] = (mins[i]<p[i]) ? mins[i] : p[i];
		maxs[i] = (maxs[i]>p[i]) ? maxs[i] : p[i];
	}	
	
	if (i==0) return NULL;
	assert(i==dim);
	return p;
}
*/

static site get_site_offline(long i) {

	if (i>=num_sites) return NULL;
	else return site_blocks[i/BLOCKSIZE]+(i%BLOCKSIZE)*dim;
}


long *shufmat;
static void make_shuffle(void){
	long i,t,j;
	static long mat_size = 0;

	if (mat_size<=num_sites) {
		mat_size = num_sites+1;
		shufmat = (long*)malloc(mat_size*sizeof(long));
	}
	for (i=0;i<=num_sites;i++) shufmat[i] = i;
	for (i=0;i<num_sites;i++){
		t = shufmat[i];
		shufmat[i] = shufmat[j = i + (num_sites-i)*(long)double_rand()];
		shufmat[j] = t;
	}
}

static long (*shuf)(long);
long noshuffle(long i) {return i;}
long shufflef(long i) {return shufmat[i];}

static site (*get_site_n)(long);
site get_next_site(void) {
	static long s_num = 0;
	return (*get_site_n)((*shuf)(s_num++));
}


static void errline(char *s) {fprintf(stderr, s); fprintf(stderr,"\n"); return;}
static void tell_options(void) {

	errline("options:");
	errline( "-m mult  multiply by mult before rounding;");
	errline( "-aa<alpha> alpha shape, alpha=<alpha>;");
}


static void echo_command_line(FILE *F, int argc, char **argv) {
	fprintf(F,"%%");
	while (--argc>=0) 
		fprintf(F, "%s%s", *argv++, (argc>0) ? " " : "");
		fprintf(F,"\n");
}

char *output_forms[] = {"vn", "ps", "mp", "cpr", "off"};

out_func *out_funcs[] = {&vlist_out, &ps_out, &mp_out, &cpr_out, &off_out};


static int set_out_func(char *s) {

	int i;

#ifdef WIN32
	if (strcmp(s, "off")==0) {
		errline("Sorry, no OFF output on WIN32");
		return 0;
	}
#endif

	for (i=0;i< sizeof(out_funcs)/(sizeof (out_func*)); i++)
		if (strcmp(s,output_forms[i])==0) return i;
	tell_options();
	return 0;
}

static void make_output(simplex *root, void *(visit_gen)(simplex*, visit_func* visit),
		visit_func* visit,
		out_func* out_funcp,
		FILE *F){

	out_funcp(0,0,F,-1);
	visit(0, out_funcp);
	visit_gen(root, visit);
	out_funcp(0,0,F,1);
	fclose(F);
}



int main(int argc, char **argv) {


	short	pine = 0,
		output = 1,
		hist = 0,
		vol = 0,
		ahull = 0,
		ofn = 0,
		ifn = 0;
	int	option;
	double	alpha = 0;
	int	main_out_form=0, alpha_out_form=0;
	simplex *root;
	fg 	*faces_gr;

	mult_up = 1;

	while ((option = getopt(argc, argv, "i:m:rs:do:X:a:Af:")) != EOF) {
		switch (option) {
		case 'm' :
			sscanf(optarg,"%lf",&mult_up);
			DEBEXP(-4,mult_up);
			break;
		case 'a' :
			vd = ahull = 1;
			switch(optarg[0]) {
				case 'a': sscanf(optarg+1,"%lf",&alpha); break;
				case '\0': break;
				default: tell_options();
			 }
			break;
		default :
			tell_options();
			exit(1);
		}
	}

	INFILE = stdin;
	OUTFILE = stdout;
	DFILE = stderr;
	read_next_site(-1);
	if (dim > MAXDIM) panic("dimension bound MAXDIM exceeded"); 

	point_size = site_size = sizeof(Coord)*dim;

	shuf = &noshuffle;
	get_site_n = read_next_site;

	root = build_convex_hull(get_next_site, site_numm, dim, vd);

	out_func* aof = out_funcs[alpha_out_form];
	
	if (alpha==0) alpha=find_alpha(root);
	alph_test(0,0,&alpha);
	make_output(root, visit_outside_ashape, afacets_print, aof, OUTFILE);

	free_hull_storage();

	exit(0);
}
