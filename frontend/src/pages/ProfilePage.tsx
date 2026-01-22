import { useState, useEffect } from 'react'
import { profileApi } from '../services/api'
import toast from 'react-hot-toast'

interface Experience {
  title: string
  duration: string
  description: string
  skills_developed: string[]
  impact: string
}

interface Profile {
  name: string
  age: number | null
  background: string
  location: string
  gpa: number | null
  sat_verbal: number | null
  activities: string[]
  achievements: string[]
  major_experiences: Experience[]
}

export default function ProfilePage() {
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [profile, setProfile] = useState<Profile>({
    name: '',
    age: null,
    background: '',
    location: '',
    gpa: null,
    sat_verbal: null,
    activities: [],
    achievements: [],
    major_experiences: [],
  })

  const [newActivity, setNewActivity] = useState('')
  const [newAchievement, setNewAchievement] = useState('')

  useEffect(() => {
    profileApi.getProfile()
      .then((data) => {
        setProfile({
          name: data.name || '',
          age: data.age,
          background: data.background || '',
          location: data.location || '',
          gpa: data.gpa,
          sat_verbal: data.sat_verbal,
          activities: data.activities || [],
          achievements: data.achievements || [],
          major_experiences: data.major_experiences || [],
        })
      })
      .catch(console.error)
      .finally(() => setLoading(false))
  }, [])

  const handleSave = async () => {
    setSaving(true)
    try {
      await profileApi.updateProfile(profile)
      toast.success('Profile saved!')
    } catch {
      toast.error('Failed to save profile')
    } finally {
      setSaving(false)
    }
  }

  const addActivity = () => {
    if (newActivity.trim()) {
      setProfile((p) => ({
        ...p,
        activities: [...p.activities, newActivity.trim()],
      }))
      setNewActivity('')
    }
  }

  const removeActivity = (index: number) => {
    setProfile((p) => ({
      ...p,
      activities: p.activities.filter((_, i) => i !== index),
    }))
  }

  const addAchievement = () => {
    if (newAchievement.trim()) {
      setProfile((p) => ({
        ...p,
        achievements: [...p.achievements, newAchievement.trim()],
      }))
      setNewAchievement('')
    }
  }

  const removeAchievement = (index: number) => {
    setProfile((p) => ({
      ...p,
      achievements: p.achievements.filter((_, i) => i !== index),
    }))
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full">
        <div className="animate-spin w-8 h-8 border-4 border-primary-500 border-t-transparent rounded-full" />
      </div>
    )
  }

  return (
    <div className="h-full overflow-y-auto">
      <div className="max-w-3xl mx-auto p-6 space-y-8">
        <div>
          <h2 className="text-2xl font-bold">Student Profile</h2>
          <p className="text-gray-600">
            Your profile helps generate personalized essays
          </p>
        </div>

        {/* Basic Info */}
        <section className="bg-white rounded-lg p-6 shadow-sm space-y-4">
          <h3 className="font-semibold text-lg">Basic Information</h3>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Full Name
              </label>
              <input
                type="text"
                value={profile.name}
                onChange={(e) => setProfile((p) => ({ ...p, name: e.target.value }))}
                className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Age
              </label>
              <input
                type="number"
                value={profile.age || ''}
                onChange={(e) => setProfile((p) => ({ ...p, age: e.target.value ? parseInt(e.target.value) : null }))}
                className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Location
              </label>
              <input
                type="text"
                value={profile.location}
                onChange={(e) => setProfile((p) => ({ ...p, location: e.target.value }))}
                placeholder="City, State"
                className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                GPA
              </label>
              <input
                type="number"
                step="0.01"
                max="5"
                value={profile.gpa || ''}
                onChange={(e) => setProfile((p) => ({ ...p, gpa: e.target.value ? parseFloat(e.target.value) : null }))}
                className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                SAT Verbal Score
              </label>
              <input
                type="number"
                max="800"
                value={profile.sat_verbal || ''}
                onChange={(e) => setProfile((p) => ({ ...p, sat_verbal: e.target.value ? parseInt(e.target.value) : null }))}
                className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500"
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Background Story
            </label>
            <textarea
              value={profile.background}
              onChange={(e) => setProfile((p) => ({ ...p, background: e.target.value }))}
              rows={4}
              placeholder="Tell us about yourself, your family, your journey..."
              className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500"
            />
          </div>
        </section>

        {/* Activities */}
        <section className="bg-white rounded-lg p-6 shadow-sm space-y-4">
          <h3 className="font-semibold text-lg">Extracurricular Activities</h3>

          <div className="flex gap-2">
            <input
              type="text"
              value={newActivity}
              onChange={(e) => setNewActivity(e.target.value)}
              placeholder="Add an activity..."
              className="flex-1 px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500"
              onKeyDown={(e) => e.key === 'Enter' && addActivity()}
            />
            <button
              onClick={addActivity}
              className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700"
            >
              Add
            </button>
          </div>

          <div className="flex flex-wrap gap-2">
            {profile.activities.map((activity, index) => (
              <span
                key={index}
                className="inline-flex items-center gap-2 px-3 py-1 bg-gray-100 rounded-full text-sm"
              >
                {activity}
                <button
                  onClick={() => removeActivity(index)}
                  className="text-gray-400 hover:text-red-500"
                >
                  ×
                </button>
              </span>
            ))}
          </div>
        </section>

        {/* Achievements */}
        <section className="bg-white rounded-lg p-6 shadow-sm space-y-4">
          <h3 className="font-semibold text-lg">Achievements & Awards</h3>

          <div className="flex gap-2">
            <input
              type="text"
              value={newAchievement}
              onChange={(e) => setNewAchievement(e.target.value)}
              placeholder="Add an achievement..."
              className="flex-1 px-4 py-2 border rounded-lg focus:ring-2 focus:ring-primary-500"
              onKeyDown={(e) => e.key === 'Enter' && addAchievement()}
            />
            <button
              onClick={addAchievement}
              className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700"
            >
              Add
            </button>
          </div>

          <div className="flex flex-wrap gap-2">
            {profile.achievements.map((achievement, index) => (
              <span
                key={index}
                className="inline-flex items-center gap-2 px-3 py-1 bg-yellow-100 rounded-full text-sm"
              >
                {achievement}
                <button
                  onClick={() => removeAchievement(index)}
                  className="text-gray-400 hover:text-red-500"
                >
                  ×
                </button>
              </span>
            ))}
          </div>
        </section>

        {/* Save button */}
        <div className="flex justify-end">
          <button
            onClick={handleSave}
            disabled={saving}
            className="px-6 py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50"
          >
            {saving ? 'Saving...' : 'Save Profile'}
          </button>
        </div>
      </div>
    </div>
  )
}
