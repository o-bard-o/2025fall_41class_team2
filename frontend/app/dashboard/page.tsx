'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { X } from 'phosphor-react'
import { getProjects, createProject, deleteProject } from '../../lib/api'
import { useAuth } from '../../components/AuthContext'

export default function Dashboard() {
    const router = useRouter()
    const { user, loading: authLoading } = useAuth()
    const [projects, setProjects] = useState<any[]>([])
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState<string | null>(null)
    const [showModal, setShowModal] = useState(false)
    const [newProject, setNewProject] = useState({ title: '', description: '' })

    useEffect(() => {
        if (!authLoading && !user) {
            router.push('/')
            return
        }

        if (user) {
            loadProjects()
        }
    }, [user, authLoading, router])

    const loadProjects = async () => {
        try {
            setLoading(true)
            const data = await getProjects()
            setProjects(data)
        } catch (err: any) {
            setError(err.message)
        } finally {
            setLoading(false)
        }
    }

    const handleCreateProject = async () => {
        if (!newProject.title.trim()) return

        try {
            const created = await createProject(newProject.title, newProject.description)
            setProjects([created, ...projects])
            setShowModal(false)
            setNewProject({ title: '', description: '' })
        } catch (err: any) {
            setError(err.message)
        }
    }

    const handleDeleteProject = async (projectId: string, e: React.MouseEvent) => {
        e.stopPropagation()

        try {
            await deleteProject(projectId)
            setProjects(projects.filter(p => p.id !== projectId))
        } catch (err: any) {
            setError(err.message)
        }
    }

    if (authLoading || loading) {
        return (
            <div className="flex min-h-screen items-center justify-center bg-white">
                <p className="text-sm text-gray-500">Loading...</p>
            </div>
        )
    }

    return (
        <div className="min-h-screen bg-white p-8">
            <div className="mx-auto max-w-6xl">
                <header className="mb-8 flex items-center justify-between">
                    <div>
                        <h1 className="text-3xl font-normal text-black">Your Projects</h1>
                        <p className="mt-1 text-sm text-gray-500">Manage your knowledge base</p>
                    </div>
                    <button
                        onClick={() => setShowModal(true)}
                        className="rounded-full border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-black transition-colors hover:bg-gray-50"
                    >
                        + New Project
                    </button>
                </header>

                {error && (
                    <div className="mb-4 rounded border border-red-200 bg-red-50 p-3 text-sm text-red-600">
                        {error}
                    </div>
                )}

                <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
                    {projects.map((project) => (
                        <div
                            key={project.id}
                            onClick={() => router.push(`/project/${project.id}`)}
                            className="group relative rounded-lg border border-gray-200 bg-white p-6 text-left transition-all hover:shadow-md"
                        >
                            <h3 className="text-lg font-medium text-black">{project.title}</h3>
                            {project.description && (
                                <p className="mt-2 text-sm text-gray-500">{project.description}</p>
                            )}
                            <p className="mt-4 text-xs text-gray-400">
                                {new Date(project.created_at).toLocaleDateString()}
                            </p>
                            <button
                                onClick={(e) => handleDeleteProject(project.id, e)}
                                className="absolute right-2 top-2 hidden rounded-full bg-white p-1.5 shadow-md hover:bg-red-50 group-hover:block"
                                title="Delete project"
                            >
                                <X size={16} weight="bold" className="text-red-600" />
                            </button>
                        </div>
                    ))}

                    <button
                        onClick={() => setShowModal(true)}
                        className="flex flex-col items-center justify-center rounded-lg border-2 border-dashed border-gray-300 bg-white p-6 transition-colors hover:bg-gray-50"
                    >
                        <div className="rounded-full bg-gray-100 p-3">
                            <svg
                                className="h-6 w-6 text-gray-400"
                                fill="none"
                                stroke="currentColor"
                                viewBox="0 0 24 24"
                            >
                                <path
                                    strokeLinecap="round"
                                    strokeLinejoin="round"
                                    strokeWidth={2}
                                    d="M12 4v16m8-8H4"
                                />
                            </svg>
                        </div>
                        <p className="mt-3 text-sm font-medium text-gray-600">Create new project</p>
                    </button>
                </div>
            </div>

            {/* Modal */}
            {showModal && (
                <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-30">
                    <div className="w-full max-w-md rounded-lg bg-white p-6 shadow-lg">
                        <h2 className="text-xl font-medium text-black">New Project</h2>
                        <div className="mt-4 space-y-4">
                            <div>
                                <label className="block text-sm font-medium text-gray-700">Title</label>
                                <input
                                    type="text"
                                    value={newProject.title}
                                    onChange={(e) => setNewProject({ ...newProject, title: e.target.value })}
                                    className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 focus:border-gray-500 focus:outline-none"
                                    placeholder="My Research Project"
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700">Description (Optional)</label>
                                <textarea
                                    value={newProject.description}
                                    onChange={(e) => setNewProject({ ...newProject, description: e.target.value })}
                                    className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2 focus:border-gray-500 focus:outline-none"
                                    rows={3}
                                    placeholder="What is this project about?"
                                />
                            </div>
                        </div>
                        <div className="mt-6 flex gap-3">
                            <button
                                onClick={handleCreateProject}
                                className="flex-1 rounded-full bg-black px-4 py-2 text-sm font-medium text-white hover:bg-gray-800"
                            >
                                Create
                            </button>
                            <button
                                onClick={() => setShowModal(false)}
                                className="flex-1 rounded-full border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-black hover:bg-gray-50"
                            >
                                Cancel
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    )
}
