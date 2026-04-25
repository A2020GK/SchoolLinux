import type { IconDefinition } from '@fortawesome/fontawesome-svg-core'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'

interface FeatureCardProps {
    icon: IconDefinition
    title: string
    description: string
}

export const FeatureCard = ({ icon, title, description }: FeatureCardProps) => {
    return (
        <div className="card">
            <div style={{ fontSize: '2.5em', marginBottom: '1rem', color: 'var(--accent-strong)' }}>
                <FontAwesomeIcon icon={icon} />
            </div>
            <h3>{title}</h3>
            <p>{description}</p>
        </div>
    )
}
