import { useEffect, useMemo, useState } from 'react';
import { AlertTriangle, CheckCircle2, Loader2, Save } from 'lucide-react';
import FileUpload from './FileUpload';
import MultiTagInput from './MultiTagInput';
import { updateProfile, uploadPrescriptionFiles } from '../../api/client';
import { useAuth } from '../../context/AuthContext';

const BLOOD_GROUPS = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-'];
const GENDER_OPTIONS = ['Male', 'Female', 'Other'];

function normalizeProfileForForm(user) {
  return {
    age: user?.age ?? '',
    blood_group: user?.blood_group ?? '',
    weight: user?.weight ?? '',
    gender: user?.gender ?? '',
    allergies: user?.allergies ?? [],
    conditions: user?.conditions ?? [],
    medications: user?.medications ?? [],
    prescription_files: user?.prescription_files ?? [],
  };
}

export default function ProfileForm() {
  const { user, setUser } = useAuth();
  const [form, setForm] = useState(normalizeProfileForForm(user));
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [saving, setSaving] = useState(false);
  const [uploading, setUploading] = useState(false);

  useEffect(() => {
    setForm(normalizeProfileForForm(user));
  }, [user]);

  const completeness = user?.profile_completeness ?? 0;
  const missingFields = user?.missing_critical_fields ?? [];

  const canSave = useMemo(() => !saving && !uploading, [saving, uploading]);

  function setField(name, value) {
    setForm((prev) => ({ ...prev, [name]: value }));
  }

  async function handleSave() {
    setSaving(true);
    setError('');
    setSuccess('');

    try {
      const payload = {
        age: form.age === '' ? null : Number(form.age),
        blood_group: form.blood_group || null,
        weight: form.weight === '' ? null : Number(form.weight),
        gender: form.gender || null,
        allergies: form.allergies,
        conditions: form.conditions,
        medications: form.medications,
        prescription_files: form.prescription_files,
      };

      const updated = await updateProfile(payload);
      setUser(updated);
      setSuccess('Profile saved successfully.');
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to save profile.');
    } finally {
      setSaving(false);
    }
  }

  async function handleUpload(files) {
    setUploading(true);
    setError('');
    setSuccess('');

    try {
      const response = await uploadPrescriptionFiles(files);
      const mergedFiles = [...form.prescription_files, ...response.uploaded_files];
      const medMap = new Map(form.medications.map((med) => [med.toLowerCase(), med]));
      (response.extracted_medications || []).forEach((med) => {
        if (!medMap.has(med.toLowerCase())) {
          medMap.set(med.toLowerCase(), med);
        }
      });

      const updated = await updateProfile({
        prescription_files: mergedFiles,
        medications: Array.from(medMap.values()),
      });
      setUser(updated);
      setSuccess('Files uploaded and profile updated.');
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to upload prescriptions.');
    } finally {
      setUploading(false);
    }
  }

  async function handleRemoveFile(index) {
    const nextFiles = form.prescription_files.filter((_, idx) => idx !== index);
    setField('prescription_files', nextFiles);
    setSaving(true);
    setError('');
    try {
      const updated = await updateProfile({ prescription_files: nextFiles });
      setUser(updated);
      setSuccess('Prescription file removed.');
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to remove file.');
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="card-padded space-y-5">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <h2 className="text-lg font-semibold text-slate-900">Health Profile</h2>
          <p className="text-sm text-slate-500">
            Keep your profile updated for more personalized AI insights.
          </p>
        </div>
        <div className="rounded-xl border border-emerald-200 bg-emerald-50 px-4 py-2 text-right">
          <p className="text-xs text-emerald-700">Profile completeness</p>
          <p className="text-lg font-bold text-emerald-700">{completeness}%</p>
        </div>
      </div>

      {missingFields.length > 0 && (
        <div className="rounded-xl border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-800">
          <div className="mb-1 flex items-center gap-2 font-semibold">
            <AlertTriangle className="h-4 w-4" />
            Missing critical profile info
          </div>
          <p className="text-xs">{missingFields.join(', ')}</p>
        </div>
      )}

      {error && (
        <div className="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
          {error}
        </div>
      )}

      {success && (
        <div className="rounded-xl border border-emerald-200 bg-emerald-50 px-4 py-3 text-sm text-emerald-700">
          <span className="inline-flex items-center gap-1">
            <CheckCircle2 className="h-4 w-4" />
            {success}
          </span>
        </div>
      )}

      <div className="grid gap-4 sm:grid-cols-2">
        <div>
          <label className="mb-1 block text-sm font-medium text-slate-700">Age</label>
          <input
            type="number"
            min={1}
            max={120}
            className="input-field"
            value={form.age}
            onChange={(event) => setField('age', event.target.value)}
          />
        </div>

        <div>
          <label className="mb-1 block text-sm font-medium text-slate-700">Blood Group</label>
          <select
            className="input-field"
            value={form.blood_group}
            onChange={(event) => setField('blood_group', event.target.value)}
          >
            <option value="">Select blood group</option>
            {BLOOD_GROUPS.map((group) => (
              <option key={group} value={group}>
                {group}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label className="mb-1 block text-sm font-medium text-slate-700">Weight (kg)</label>
          <input
            type="number"
            min={1}
            step="0.1"
            className="input-field"
            value={form.weight}
            onChange={(event) => setField('weight', event.target.value)}
            placeholder="e.g. 68.5"
          />
        </div>

        <div>
          <label className="mb-1 block text-sm font-medium text-slate-700">Gender</label>
          <select
            className="input-field"
            value={form.gender}
            onChange={(event) => setField('gender', event.target.value)}
          >
            <option value="">Select gender</option>
            {GENDER_OPTIONS.map((option) => (
              <option key={option} value={option}>
                {option}
              </option>
            ))}
          </select>
        </div>
      </div>

      <MultiTagInput
        id="allergies"
        label="Known Allergies"
        values={form.allergies}
        onChange={(next) => setField('allergies', next)}
        placeholder="Type and press Enter (e.g. pollen)"
        helperText="Used to avoid risky medication suggestions."
      />

      <MultiTagInput
        id="conditions"
        label="Existing Conditions"
        values={form.conditions}
        onChange={(next) => setField('conditions', next)}
        placeholder="Type and press Enter (e.g. diabetes)"
      />

      <MultiTagInput
        id="medications"
        label="Current Medications"
        values={form.medications}
        onChange={(next) => setField('medications', next)}
        placeholder="Type and press Enter (e.g. metformin)"
      />

      <FileUpload
        files={form.prescription_files}
        onUpload={handleUpload}
        onRemove={handleRemoveFile}
        isUploading={uploading}
      />

      <button
        type="button"
        onClick={handleSave}
        disabled={!canSave}
        className="btn-primary w-full sm:w-auto"
      >
        {saving ? <Loader2 className="h-4 w-4 animate-spin" /> : <Save className="h-4 w-4" />}
        {saving ? 'Saving...' : 'Save Health Profile'}
      </button>
    </div>
  );
}
