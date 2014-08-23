#include <stdlib.h>
#include <stdio.h>
#include <math.h>
#include <string.h>

//will make these configurable
float constant;
float multiplier;

//could return this struct
struct info
{
	float minX;
	float minY;
	float maxX;
	float maxY;

	int width;
	int height;
        int cPixels;
	int dotsize;

        float maxF;
        float minF;
};

struct point {
    float x;
    float y;
};

#ifdef WIN32
#define WIN32_LEAN_AND_MEAN
#include <Windows.h>

BOOL WINAPI DllMain(    HINSTANCE hinstDLL,  // handle to DLL module
                        DWORD fdwReason,     // reason for calling function
                        LPVOID lpReserved )  // reserved
{
    return TRUE;
}
#endif

//walk the list of points, get the boundary values    
void getBounds(struct info *inf, float *points, unsigned int cPoints, int weighted)
{
    unsigned int i = 0;

    // first init the global counts
    float minX = points[i];
    float minY = points[i+1];
    float maxX = points[i];
    float maxY = points[i+1];

    int inc = 2;
    if (weighted) inc = 3;

    //then iterate over the list and find the max/min values
    for(i = 0; i < cPoints; i=i+inc)
    {
        float x = points[i];
        float y = points[i+1];

        if (x > maxX) maxX = x;
        if (x < minX) minX = x;

        if (y > maxY) maxY = y;
        if (y < minY) minY = y;
    }
    
    inf->minX = minX;
    inf->minY = minY;
    inf->maxX = maxX;
    inf->maxY = maxY;

    return;
}

//transform from dataset coordinates into image coordinates
struct point translate(struct info *inf, struct point pt)
{
    float minX = inf->minX;
    float minY = inf->minY;
    float maxX = inf->maxX;
    float maxY = inf->maxY;
    
    int width = inf->width;
    int height = inf->height;
       
    // normalize the point into range 0..1
    pt.x = (pt.x - minX) / (maxX - minX);
    pt.y = (pt.y - minY) / (maxY - minY);

    //and then map into our image dimentions.
    pt.x = (pt.x * width);
    pt.y = ((1-pt.y) * height);

    return pt;
}

unsigned char* normalise(struct info *inf, float *floatArray, int cFloats){

    //create pixels array, no need to clear as will run over full array and set everything
    unsigned char* pixels = (unsigned char *)malloc(cFloats*sizeof(char));
    int i = 0;

    //find the max and min values in the array     
    float minF = floatArray[0];
    float maxF = floatArray[0];
    float f;

    for (i = 1; i < cFloats; i++)
    {
        f = floatArray[i];

        if (f > maxF) maxF = f;
        if (f < minF) minF = f;
    }
    //save for later so we can query for scale
    inf->maxF = maxF;
    inf->minF = minF;

    //normalise, could add functions before such as log etc
    //keeping with initial colorize and schemes where 0 is the max value
    for (i = 0; i < cFloats; i++){
      pixels[i] = 255 - (floatArray[i] - minF)/(maxF-minF)*255;
    }

    return pixels;

}

float* calcDensity(struct info *inf, float *points, int cPoints, int weighted)
{
    int width = inf->width;
    int height = inf->height;
    int cPixels = inf->cPixels;
    int dotsize = inf->dotsize;
    
    //create the float array, maloc as initialise to floats later
    float* pixels = (float *)malloc(cPixels*sizeof(float)); 

    float midpt = dotsize / 2.f;
    float radius = sqrt(midpt*midpt + midpt*midpt) / 2.f;
    float dist = 0.f;
    float pixVal = 0.f;

    int j = 0;
    int k = 0;
    int i = 0;
    int ndx = 0;
    struct point pt = {0};  

    int inc = 2;
    if (weighted) inc = 3;

    // initialize image data to black
    for(i = 0; i < cPixels; i++) 
    {
        pixels[i] = 0.f;
    }

    for(i = 0; i < cPoints; i=i+inc)
    {
        pt.x = points[i];
        pt.y = points[i+1];
        pt = translate(inf, pt);

        for (j = (int)pt.x - midpt; j < (int)pt.x + midpt; j++)
        {   
            for (k = (int)(pt.y - midpt); k < (int)(pt.y + midpt); k++)
            {
                if (j < 0 || k < 0 || j >= width || k >= height) continue; 

                dist = sqrt( (j-pt.x)*(j-pt.x) + (k-pt.y)*(k-pt.y) );
                
                if(dist>radius) continue; // stop point contributing to pixels outside its radius
           
                ndx = k*width + j;
                if(ndx >= (int)width*height) continue;   // ndx can be greater than array bounds

                ndx = k*width + j;
                if(ndx >= cPixels) continue;   // ndx can be greater than array bounds

                if(weighted)
                {
                  pixVal = points[i+2];
                }
                else
                {
                  pixVal = 1;
                }
                //if constant == multiplier == 0 or dist == 0 want pixVal == pixVal
                //could have another function here such a quadratic, exponential decay etc.
                pixVal = pixVal-pixVal*(multiplier*dist+constant);
                //don't want to go into the negatives
                if(pixVal < 0){
                  pixVal = 0;
                }

                #ifdef DEBUG
                printf("pt.x: %.2f pt.y: %.2f j: %d k: %d ndx: %d\n", pt.x, pt.y, j, k, ndx);
                #endif 

                //simple addition for combination function
                pixels[ndx] = pixels[ndx] + pixVal;
            } // for k
        } //for j
    } // for i

    return pixels;
}

unsigned char *colorize(struct info *inf, unsigned char* pixels_bw, int *scheme, unsigned char* pixels_color, 
              int opacity)
{
    int cPixels = inf->cPixels;
    
    int i = 0;
    int pix = 0;
    int highCount = 0;
    int alpha = opacity;

    for(i = 0; i < cPixels; i++)
    {
        pix = pixels_bw[i];

        if (pix < 0x10) highCount++;
        //make tunable
        if (pix <= 252) 
            alpha = opacity; 
        else 
            alpha = 0;

        pixels_color[i*4] = scheme[pix*3];
        pixels_color[i*4+1] = scheme[pix*3+1];
        pixels_color[i*4+2] = scheme[pix*3+2];
        pixels_color[i*4+3] = alpha;
    } 
    
    if (highCount > cPixels*0.8)
    {   
        fprintf(stderr, "Warning: 80%% of output pixels are over 95%% density.\n");
        fprintf(stderr, "Decrease dotsize or increase output image resolution?\n");
    }

    return pixels_color;
}

#ifdef WIN32
__declspec(dllexport)
#endif
unsigned char *tx(float *points, 
                  int cPoints, 
                  int w, int h, 
                  int dotsize, 
                  int *scheme, 
                  unsigned char *pix_color, 
                  int opacity, 
                  int boundsOverride, 
                  float minX, float minY, float maxX, float maxY,
                  int weighted, float mult, float cnst)
{
    unsigned char *pixels_bw = NULL;
    float *floats_bw = NULL;
    struct info inf = {0};

    //basic sanity checks to keep from segfaulting
    if (NULL == points || NULL == scheme || NULL == pix_color ||
        w <= 0 || h <= 0 || cPoints <= 1+weighted || cPoints % (2+weighted) != 0 ||
        opacity < 0 || opacity > 255 || dotsize <= 0)
    {
        fprintf(stderr, "Invalid parameter; aborting.\n");
        return NULL;
    }
    
    inf.dotsize = dotsize;
    inf.width = w;
    inf.height = h;
    inf.cPixels = w*h;

    multiplier = mult;
    constant = cnst;
 
    // get min/max x/y values from point list
    if (boundsOverride == 1)
    {
        inf.maxX = maxX; inf.minX = minX;
        inf.maxY = maxY; inf.minY = minY;
    }
    else
    {
        getBounds(&inf, points, cPoints, weighted);
    }

    #ifdef DEBUG
    printf("min: (%.2f, %.2f) max: (%.2f, %.2f)\n", inf.minX, inf.minY, inf.maxX, inf.maxY);
    #endif

    //iterate through points, place a dot at each center point
    //and set pix value using multiply method for radius [dotsize] and 
    //addition with any prevoius values
    floats_bw = calcDensity(&inf, points, cPoints, weighted);
    //normalise the float numbers to char values between 0 and 255
    pixels_bw = normalise(&inf, floats_bw, w*h);
    //no longer need the floats
    free(floats_bw);
    floats_bw = NULL;
    //using provided color scheme and opacity, update pixel value to RGBA values
    pix_color = colorize(&inf, pixels_bw, scheme, pix_color, opacity);
    //no longer need the 0-255 pixels
    free(pixels_bw);
    pixels_bw = NULL;

    //return list of RGBA values
    return pix_color;
}
