import { useOutletContext } from 'react-router-dom';
import DiseasePrediction from './DiseasePrediction';

export default function DiseasePredictionPage() {
  const { symptoms } = useOutletContext();
  return <DiseasePrediction symptoms={symptoms || []} />;
}
