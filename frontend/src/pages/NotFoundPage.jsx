import React from 'react';
import { useNavigate } from 'react-router-dom';
import Container from '../components/Container';
import Button from '../components/Button';

export default function NotFoundPage() {
  const navigate = useNavigate();

  return (
    <div className="pt-32 pb-16 min-h-screen flex items-center justify-center">
      <Container size="compact">
        <div className="bg-white rounded-3xl sm:rounded-[2.5rem] border border-gray-200/90 p-8 sm:p-12 text-center max-w-md mx-auto shadow-xs">
          <span className="font-display font-extrabold text-6xl text-[#0a152d]">
            404
          </span>
          <h1 className="font-display font-bold text-2xl text-[#0a1b33] mt-2">
            Page Not Found
          </h1>
          <p className="text-sm text-gray-500 mt-2 mb-6">
            The page you are looking for does not exist or has been moved.
          </p>
          <Button variant="primary" onClick={() => navigate('/')}>
            Back to Home
          </Button>
        </div>
      </Container>
    </div>
  );
}
