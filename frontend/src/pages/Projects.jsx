import React, { useEffect } from 'react'
import { projectService } from '../services'
import { useApi } from '../hooks/useApi'
import './Projects.css'

const Projects = () => {
  const { data: projects, loading, error, execute: fetchProjects } = useApi(projectService.getProjects)

  useEffect(() => {
    fetchProjects()
  }, [fetchProjects])

  if (loading) {
    return (
      <div className="page-container">
        <div style={{ textAlign: 'center', padding: '40px' }}>Loading...</div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="page-container">
        <div className="error-message">Error: {error}</div>
      </div>
    )
  }

  return (
    <div className="page-container">
      <div className="page-header">
        <h1>Projects</h1>
        <p>Manage your annotation projects</p>
      </div>

      <div className="projects-grid">
        {projects && projects.map((project) => (
          <div key={project.id} className="project-card">
            <h3>{project.name}</h3>
            <p className="project-description">{project.description || 'No description'}</p>
            <div className="project-meta">
              <span>Created: {new Date(project.created_at).toLocaleDateString()}</span>
            </div>
          </div>
        ))}

        {projects.length === 0 && (
          <div className="empty-state">
            <p>No projects found</p>
          </div>
        )}
      </div>
    </div>
  )
}

export default Projects
