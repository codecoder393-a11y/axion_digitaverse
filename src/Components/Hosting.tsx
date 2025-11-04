
import React, { useState } from 'react';
import { useUser } from '../UserContext';
import './Hosting.css';

const Hosting: React.FC = () => {
    const { user } = useUser();
    const [websites, setWebsites] = useState([
        { id: 1, name: 'My Personal Blog', transactionId: 'dummy-tx-1' },
        { id: 2, name: 'Project Portfolio', transactionId: 'dummy-tx-2' },
    ]);
    const [selectedFile, setSelectedFile] = useState<File | null>(null);
    const [uploading, setUploading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
        if (event.target.files) {
            setSelectedFile(event.target.files[0]);
        }
    };

    const handleUpload = async () => {
        if (selectedFile && user) {
            setUploading(true);
            setError(null);

            const formData = new FormData();
            formData.append('file', selectedFile);

            try {
                const response = await fetch('/api/store-file', {
                    method: 'POST',
                    headers: {
                        'X-Address': user.address,
                        'X-Token': user.token,
                    },
                    body: formData,
                });

                if (response.ok) {
                    const data = await response.json();
                    const newWebsite = {
                        id: websites.length + 1,
                        name: selectedFile.name,
                        transactionId: data.block.data[0].id,
                    };
                    setWebsites([...websites, newWebsite]);
                    setSelectedFile(null);
                } else {
                    const errorData = await response.json();
                    setError(errorData.error || 'Upload failed');
                }
            } catch (err) {
                setError('An error occurred during upload.');
            } finally {
                setUploading(false);
            }
        }
    };

    return (
        <div className="hosting-container">
            <div className="upload-section">
                <h2>Upload Your Website</h2>
                <input type="file" onChange={handleFileChange} />
                <button onClick={handleUpload} disabled={!selectedFile || uploading}>
                    {uploading ? 'Uploading...' : 'Upload'}
                </button>
                {error && <div className="error-message">{error}</div>}
            </div>
            <div className="websites-section">
                <h2>Hosted Websites</h2>
                <ul className="website-list">
                    {websites.map((website) => (
                        <li key={website.id} className="website-item">
                            <span className="website-name">{website.name}</span>
                            <a href={`/api/retrieve-file/${website.transactionId}`} target="_blank" rel="noopener noreferrer" className="view-button">
                                View
                            </a>
                        </li>
                    ))}
                </ul>
            </div>
        </div>
    );
};

export default Hosting;
