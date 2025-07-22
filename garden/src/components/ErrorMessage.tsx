interface ErrorMessageProps {
  message?: string;
}

export const ErrorMessage: React.FC<ErrorMessageProps> = ({
  message = "Fehler beim Laden der Gartendaten"
}) => {
  return (
    <div style={{
      display: 'flex',
      justifyContent: 'center',
      alignItems: 'center',
      height: '400px',
      fontSize: '18px',
      color: 'red'
    }}>
      {message}
    </div>
  );
};
