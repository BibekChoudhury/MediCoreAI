import { useState, useRef } from 'react';
import { motion } from 'framer-motion';
import {
  AlertTriangle,
  CheckCircle2,
  Stethoscope,
  Mic,
  Square,
  Upload,
  Image,
  Loader2,
  Volume2,
  MessageSquare,
  FileAudio,
} from 'lucide-react';
import clsx from 'clsx';
import { fullConsultation, textToSpeech } from '../api/client';

export default function Consultation() {
  const [audioFile, setAudioFile] = useState(null);
  const [imageFile, setImageFile] = useState(null);
  const [imagePreview, setImagePreview] = useState(null);
  const [transcription, setTranscription] = useState('');
  const [analysis, setAnalysis] = useState('');
  const [responseAudio, setResponseAudio] = useState(null);
  const [personalizedInsights, setPersonalizedInsights] = useState([]);
  const [personalizedWarnings, setPersonalizedWarnings] = useState([]);
  const [personalizedRecommendations, setPersonalizedRecommendations] = useState([]);
  const [insightLabel, setInsightLabel] = useState('Personalized Insight');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [isRecording, setIsRecording] = useState(false);

  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);
  const audioRef = useRef(null);

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaRecorderRef.current = new MediaRecorder(stream);
      audioChunksRef.current = [];

      mediaRecorderRef.current.ondataavailable = (e) => audioChunksRef.current.push(e.data);
      mediaRecorderRef.current.onstop = () => {
        const blob = new Blob(audioChunksRef.current, { type: 'audio/wav' });
        setAudioFile(new File([blob], 'recording.wav', { type: 'audio/wav' }));
        stream.getTracks().forEach((t) => t.stop());
      };

      mediaRecorderRef.current.start();
      setIsRecording(true);
    } catch (err) {
      setError('Microphone access denied: ' + err.message);
    }
  };

  const stopRecording = () => {
    mediaRecorderRef.current?.stop();
    setIsRecording(false);
  };

  const handleImageUpload = (e) => {
    const file = e.target.files[0];
    if (!file) return;
    setImageFile(file);
    setImagePreview(URL.createObjectURL(file));
  };

  const handleAudioUpload = (e) => {
    const file = e.target.files[0];
    if (file) setAudioFile(file);
  };

  const handleConsult = async () => {
    if (!audioFile && !imageFile) {
      setError('Please provide at least voice input or a medical image.');
      return;
    }
    setLoading(true);
    setError(null);
    setPersonalizedInsights([]);
    setPersonalizedWarnings([]);
    setPersonalizedRecommendations([]);
    try {
      const fd = new FormData();
      if (audioFile) fd.append('audio', audioFile);
      if (imageFile) fd.append('image', imageFile);

      const data = await fullConsultation(fd);
      setTranscription(data.transcription);
      setAnalysis(data.analysis);
      setPersonalizedInsights(data.personalized_insights || []);
      setPersonalizedWarnings(data.personalized_warnings || []);
      setPersonalizedRecommendations(data.personalized_recommendations || []);
      setInsightLabel(data.personalized_insight_label || 'Personalized Insight');

      if (data.response_audio) {
        const blob = new Blob(
          [Uint8Array.from(atob(data.response_audio), (c) => c.charCodeAt(0))],
          { type: 'audio/mpeg' },
        );
        setResponseAudio(URL.createObjectURL(blob));
      }
    } catch (err) {
      setError(err.response?.data?.error || 'Consultation failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleSpeak = async (text) => {
    try {
      const data = await textToSpeech(text);
      if (data.audio) {
        const blob = new Blob(
          [Uint8Array.from(atob(data.audio), (c) => c.charCodeAt(0))],
          { type: 'audio/mpeg' },
        );
        new Audio(URL.createObjectURL(blob)).play();
      }
    } catch {
      /* silent */
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <div className="flex items-center gap-2 mb-1">
          <Stethoscope className="h-5 w-5 text-emerald-600" />
          <h1 className="text-xl font-bold text-slate-900">AI Doctor Consultation</h1>
        </div>
        <p className="text-sm text-slate-500">
          Record your voice and/or upload a medical image for AI-powered analysis.
        </p>
      </div>

      {/* Error */}
      {error && (
        <div className="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
          {error}
        </div>
      )}

      {/* Input Cards */}
      <div className="grid gap-4 sm:grid-cols-2">
        {/* Voice */}
        <div className="card-padded space-y-4">
          <div className="flex items-center gap-2">
            <Mic className="h-4 w-4 text-slate-500" />
            <h3 className="text-sm font-semibold text-slate-700">Voice Input</h3>
          </div>

          <button
            onClick={isRecording ? stopRecording : startRecording}
            disabled={loading}
            className={clsx(
              'flex w-full items-center justify-center gap-2 rounded-xl px-4 py-3 text-sm font-semibold transition-colors',
              isRecording
                ? 'bg-red-600 text-white hover:bg-red-500 animate-pulse'
                : 'bg-slate-100 text-slate-700 hover:bg-slate-200',
            )}
          >
            {isRecording ? (
              <>
                <Square className="h-4 w-4" fill="currentColor" /> Stop Recording
              </>
            ) : (
              <>
                <Mic className="h-4 w-4" /> Start Recording
              </>
            )}
          </button>

          <label className="btn-secondary w-full cursor-pointer text-center">
            <Upload className="h-4 w-4" />
            Upload Audio File
            <input
              type="file"
              accept="audio/*"
              onChange={handleAudioUpload}
              className="hidden"
              disabled={loading}
            />
          </label>

          {audioFile && (
            <div className="flex items-center gap-2 rounded-lg bg-emerald-50 px-3 py-2 text-xs text-emerald-700">
              <FileAudio className="h-3.5 w-3.5" />
              {audioFile.name}
            </div>
          )}
        </div>

        {/* Image */}
        <div className="card-padded space-y-4">
          <div className="flex items-center gap-2">
            <Image className="h-4 w-4 text-slate-500" />
            <h3 className="text-sm font-semibold text-slate-700">Medical Image</h3>
          </div>

          <label className="flex cursor-pointer flex-col items-center justify-center rounded-xl border-2 border-dashed border-slate-200 bg-slate-50 px-4 py-8 text-center transition-colors hover:border-emerald-300 hover:bg-emerald-50/30">
            {imagePreview ? (
              <img
                src={imagePreview}
                alt="Preview"
                className="max-h-36 rounded-lg object-contain"
              />
            ) : (
              <>
                <Image className="mb-2 h-8 w-8 text-slate-300" />
                <p className="text-sm font-medium text-slate-500">Click to upload</p>
                <p className="text-xs text-slate-400">JPG, PNG supported</p>
              </>
            )}
            <input
              type="file"
              accept="image/*"
              onChange={handleImageUpload}
              className="hidden"
              disabled={loading}
            />
          </label>

          {imageFile && (
            <div className="flex items-center gap-2 rounded-lg bg-emerald-50 px-3 py-2 text-xs text-emerald-700">
              <Image className="h-3.5 w-3.5" />
              {imageFile.name}
            </div>
          )}
        </div>
      </div>

      {/* Consult Button */}
      <div className="flex justify-center">
        <button
          onClick={handleConsult}
          disabled={loading || (!audioFile && !imageFile)}
          className="btn-primary px-8 py-3 text-base"
        >
          {loading ? (
            <Loader2 className="h-5 w-5 animate-spin" />
          ) : (
            <Stethoscope className="h-5 w-5" />
          )}
          {loading ? 'Processing…' : 'Get AI Consultation'}
        </button>
      </div>

      {/* Results */}
      {(transcription || analysis) && (
        <motion.div
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          className="space-y-4"
        >
          {(personalizedInsights.length > 0 || personalizedWarnings.length > 0) && (
            <div className="rounded-xl border border-emerald-200 bg-emerald-50 px-5 py-4">
              <h4 className="mb-2 text-sm font-semibold text-emerald-800">{insightLabel}</h4>

              {personalizedInsights.length > 0 && (
                <ul className="space-y-1.5">
                  {personalizedInsights.map((item, idx) => (
                    <li key={idx} className="flex items-start gap-2 text-xs text-emerald-800">
                      <CheckCircle2 className="mt-0.5 h-3.5 w-3.5 shrink-0 text-emerald-600" />
                      {item}
                    </li>
                  ))}
                </ul>
              )}

              {personalizedWarnings.length > 0 && (
                <ul className="mt-2 space-y-1.5">
                  {personalizedWarnings.map((item, idx) => (
                    <li key={idx} className="flex items-start gap-2 text-xs text-amber-800">
                      <AlertTriangle className="mt-0.5 h-3.5 w-3.5 shrink-0 text-amber-600" />
                      {item}
                    </li>
                  ))}
                </ul>
              )}
            </div>
          )}

          {transcription && (
            <div className="card-padded">
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-2">
                  <MessageSquare className="h-4 w-4 text-blue-500" />
                  <h4 className="text-sm font-semibold text-slate-700">Your Question</h4>
                </div>
                <button
                  onClick={() => handleSpeak(transcription)}
                  className="btn-secondary py-1.5 px-3 text-xs"
                >
                  <Volume2 className="h-3.5 w-3.5" /> Listen
                </button>
              </div>
              <p className="text-sm leading-relaxed text-slate-600">{transcription}</p>
            </div>
          )}

          {analysis && (
            <div className="card overflow-hidden">
              <div className="bg-gradient-to-r from-emerald-600 to-teal-600 px-5 py-3">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2 text-white">
                    <Stethoscope className="h-4 w-4" />
                    <h4 className="text-sm font-semibold">AI Doctor&apos;s Analysis</h4>
                  </div>
                  <button
                    onClick={() => handleSpeak(analysis)}
                    className="rounded-lg bg-white/20 px-3 py-1 text-xs font-medium text-white hover:bg-white/30 transition-colors"
                  >
                    <Volume2 className="mr-1 inline h-3.5 w-3.5" /> Play
                  </button>
                </div>
              </div>
              <div className="px-5 py-5">
                <p className="text-sm leading-relaxed text-slate-600 whitespace-pre-wrap">
                  {analysis}
                </p>
              </div>
            </div>
          )}

          {responseAudio && (
            <div className="card-padded text-center">
              <h4 className="text-sm font-semibold text-slate-700 mb-3">Audio Response</h4>
              <audio ref={audioRef} src={responseAudio} controls className="mx-auto" />
            </div>
          )}

          {personalizedRecommendations.length > 0 && (
            <div className="card-padded">
              <h4 className="mb-3 text-sm font-semibold text-slate-800">Based on your profile</h4>
              <ul className="space-y-2">
                {personalizedRecommendations.map((item, idx) => (
                  <li key={idx} className="text-sm text-slate-600">
                    - {item}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </motion.div>
      )}

      {/* Disclaimer */}
      <div className="rounded-xl border border-amber-200 bg-amber-50 px-5 py-4">
        <p className="text-xs leading-relaxed text-amber-800">
          <strong className="font-semibold">Medical Disclaimer:</strong> This AI consultation is
          for educational purposes only. Always consult qualified healthcare professionals for
          proper diagnosis and treatment.
        </p>
      </div>
    </div>
  );
}
