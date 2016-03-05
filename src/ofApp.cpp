#include "ofApp.h"
#include "dsl_wrapper.h"

ofApp::ofApp(int argc, char ** argv){
	this->argc = argc;
	this->argv = argv;
}

void ofApp::setup(){
	ofLog() << "Running setup()";

	try{
		Py_Initialize();
		PySys_SetArgv(argc, argv);

		PyImport_AppendInittab("core", &dsl::initcore);

		vision = py::import("py.vision").attr("Vision")();
	}catch(py::error_already_set){
		PyErr_Print();
	}

	ofSetVerticalSync(true);
	ofEnableDepthTest();

	camera.setDistance(1);
	camera.setNearClip(0.01);

	dsl::colors::setup();

	ofSetEscapeQuitsApp(false);
	oscReceiver.setup(7172);

    int nOutputs = 2;
    int nInputs = 2;

    onset.setup();
    beat.setup();

    ofAddListener(onset.gotOnset, this, &ofApp::onsetEvent);
    ofAddListener(beat.gotBeat, this, &ofApp::beatEvent);

    ofSoundStreamSetup(nOutputs, nInputs, this);
}

void ofApp::exit(){
    ofSoundStreamStop();
    ofSoundStreamClose();
}

void ofApp::audioIn(float * input, int bufferSize, int nChannels){
    onset.audioIn(input, bufferSize, nChannels);
    beat.audioIn(input, bufferSize, nChannels);
}

void ofApp::update(){
	while(oscReceiver.hasWaitingMessages()){
		// get the next message
		ofxOscMessage m;
		oscReceiver.getNextMessage(m);

		if(m.getAddress() == "/code"){
			string code = m.getArgAsString(0);
			ofLog() << "OSC mesage:" << endl << "/code" << endl << code;
			try{
				vision.attr("update")(code);
			}catch(py::error_already_set){
				PyErr_Print();
			}
		}
	}
}

void ofApp::draw(){
	camera.begin();
	try{
		vision.attr("draw")();
	}catch(py::error_already_set){
		PyErr_Print();
	}
	camera.end();

	string fps = "FPS: " + ofToString(ofGetFrameRate());
	ofSetColor(255);
	ofDrawBitmapString(fps, 10, 20);
}

void ofApp::onsetEvent(float & time) {
	dsl::audio::set_onset();
}

void ofApp::beatEvent(float & time) {
	dsl::audio::set_beat();
}
