import React from 'react';
import ProgressIndicator from './ProgressIndicator';

export default function LoadingState({ step = 2 }) {
  return (
    <div className="py-12 flex flex-col items-center justify-center">
      <ProgressIndicator currentStep={step} />
    </div>
  );
}
