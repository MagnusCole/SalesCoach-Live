import CoachLive from '@/components/CoachLive';
import { CoachProvider } from '@/contexts/CoachContext';

export default function Home() {
  return (
    <CoachProvider>
      <CoachLive />
    </CoachProvider>
  );
}
