////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
//  lvmodule TTS Synthesis Interface for Python
//
//	Description :
//	This is a simple bridge between python apps and the LumenVox TTS Server.
//  A python statement like this:
// 		mp3= lv.tts("Hello World")
//	would use the HTTSCLIENT to access the LumenVox TTS server to generate a raw PCM synthesise of the provided text
//  using the lame mp3 encoder, the PCM samples are converted into mp3 (look for the convert function for details) 	
//	and an unsigned char array containing the mp3 raw date is returned to the python caller.
//  	
//	
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

#include <Python.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <LV_TTS.h>
#include <LV_SRE.h>
#include <lame.h>
#include <malloc.h>

// declare local C functions 
unsigned char* synthesize(const char *text, int* mp3_size);
unsigned char* convert(short int *buffer, int num_bytes, int* mp3_size);
int saveToFile(unsigned char *buffer, int size, const char *fileName);

#ifdef WIN32
#define stricmp _stricmp
#else //linux
#define stricmp strcasecmp
#endif

//
//  Python-Interface
// 	tts Function to be called from Python, like so: 
// 
//  import lv
// 	mp3= lv.tts("Hello World")
//
static PyObject* lv_tts(PyObject* self, PyObject* args) {
	const char *text;
    if (!PyArg_ParseTuple(args, "s", &text)) {
        return NULL;
	} else {
		int mp3_size;
		unsigned char* mp3= synthesize(text, &mp3_size);
		return Py_BuildValue("s#", (char*)mp3, mp3_size);
	}
}

//
//  Python-Interface
//	Method mapping table, an array of PyMethodDef structures
//
static PyMethodDef module_methods[] = {
   { "tts", (PyCFunction)lv_tts, METH_VARARGS, NULL },{NULL}
};

//
//  Python-Interface
//	This function is called by the Python interpreter when the module is loaded.
//
PyMODINIT_FUNC initlv(void) {
	(void) Py_InitModule("lv", module_methods);
	LV_SRE_Startup();
}


//
// main function synthesizes standard demo text into mp3 and saves file as demo.mp3
//
int main(int argc, char * argv[]) {
	const char* demoText= "Hello world. This is a sample of the audio produced by the LumenVox T T S server.";
	const char* fileName= "demo.mp3";
	//
	//	Initialize LumenVox API
	//
	LV_SRE_Startup();

	//
	// Synthesize test string into MP3
	//
	int mp3_size;
	unsigned char* p = synthesize(demoText, &mp3_size);
	printf("Synthesized demo text into MP3 buffer.\n");
	printf("MP3 size: %d\n", mp3_size);
	int k = saveToFile(p, mp3_size, fileName);
	free(p);
	
	//	
	//  Gracefully shuts down LumenVox API and threads and flushes the logs.
	//
	LV_SRE_Shutdown();
	fflush(stdout);
	return k;
}

//
//	Synthesizes text into raw PCM and eventually into MP3 
//  returns a unsigned char * to the new mp3 raw data, 
//  mp3_size is set to the mp3 buffer size
unsigned char* synthesize(const char *text, int* mp3_size) {
	HTTSCLIENT ttsClient;
	unsigned char* synthesized_audio_buffer = NULL;
	unsigned char* mp3 = NULL; 
	int ReturnValue = -1;
	int bytes_returned = 0;
	int TotalSynthesizedAudioBytes = 0;	
	int SynthesizedSoundFormat = SFMT_PCM;
	
	ttsClient = LV_TTS_CreateClient(NULL, NULL, NULL, 0, &ReturnValue);
	ReturnValue = LV_TTS_SetPropertyEx(ttsClient, PROP_EX_SYNTH_SOUND_FORMAT, PROP_EX_VALUE_TYPE_INT_PTR, &SynthesizedSoundFormat, PROP_EX_TARGET_PORT);
	ReturnValue = LV_TTS_Synthesize(ttsClient, text, LV_TTS_BLOCK);
	ReturnValue = LV_TTS_GetSynthesizedAudioBufferLength(ttsClient, &TotalSynthesizedAudioBytes);

	synthesized_audio_buffer = malloc(TotalSynthesizedAudioBytes);

	ReturnValue = LV_TTS_GetSynthesizedAudioBuffer(ttsClient, synthesized_audio_buffer, TotalSynthesizedAudioBytes, &bytes_returned);
	ReturnValue = LV_TTS_DestroyClient(ttsClient);
		
	mp3 = convert ((short int*)(synthesized_audio_buffer), TotalSynthesizedAudioBytes, mp3_size);
	free(synthesized_audio_buffer);
	return mp3;
}

//
//	Convert a ram PCM buffer to MP3.
//  returns a unsigned char * to the new mp3 raw data, 
//  mp3_size is set to the mp3 buffer size
//	
unsigned char *convert(short int *buffer, int num_bytes, int* mp3_size) {
	// number of samples in raw pcm audio 
	const int num_samples = num_bytes>>1; 

    // worst case buffer size for mp3 buffer
	const int MP3_SIZE = 1.25 * num_samples + 7200;

	//short int pcm_buffer[PCM_SIZE];
	unsigned char* mp3_buffer= malloc(MP3_SIZE);

	const lame_t lame = lame_init();
	if ( lame == NULL ) {
		printf("Unable to initialize MP3 encoder LAME\n");
    	return NULL;
	} 

	lame_set_num_channels(lame,1);
	lame_set_in_samplerate(lame,8000);
	lame_set_out_samplerate(lame, 8000);
	lame_set_brate(lame,128);
	lame_set_mode(lame,MONO);
	lame_set_quality(lame,2);  
	lame_set_bWriteVbrTag(lame, 0);
	lame_set_VBR(lame, vbr_default);
	if ( lame_init_params(lame) < 0 ) {
		printf("Unable to initialize MP3 parameters\n");
    	return NULL;
	} 

	short size;
	size = lame_encode_buffer(lame, buffer, buffer, num_samples, mp3_buffer, MP3_SIZE);
	size+= lame_encode_flush(lame, mp3_buffer+size, MP3_SIZE);
	lame_close(lame);
	*mp3_size = size;
	return realloc(mp3_buffer,size);
}

//
//	Save buffer to file
//
int saveToFile(unsigned char* buffer, int size, const char* fileName) {
	FILE *outFile = fopen(fileName, "w+b");
	
	if(outFile == NULL) {
		printf("Problem opening file %s for writing.\n", fileName);
		return -1;
	} else {		
		int e= fwrite(buffer, sizeof(char), size, outFile);
		if (0>e) {
			printf("Problem writing to file %s.\n", fileName);
		}
		fseek(outFile, 0, SEEK_END);
		printf("Synthesized Audio file saved to %s (%d bytes)\n", fileName, (int)ftell(outFile));
		fclose(outFile);
	}
	return 0;
}
