import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import DatePicker from 'react-datepicker'
import 'react-datepicker/dist/react-datepicker.css'
import '../App.css'
import { apiGet } from '../utils/apiClient'

function ReviewsList() {
  const navigate = useNavigate()
  const [reviews, setReviews] = useState([])
  const [filteredReviews, setFilteredReviews] = useState([])
  const [loading, setLoading] = useState(true)
  const [startDate, setStartDate] = useState(null)
  const [endDate, setEndDate] = useState(null)

  useEffect(() => {
    const fetchReviews = async () => {
      try {
        const user_id = window.location.pathname.split('/')[2]
        const url = user_id 
          ? `/users/${user_id}/reviews`
          : `/reviews`
        const response = await apiGet(url)
        let data = await response.json()
        data = data.sort((a, b) => new Date(b.date_time) - new Date(a.date_time))
        setReviews(data)
        setFilteredReviews(data)
      } catch (error) {
        console.error('Error fetching reviews:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchReviews()
  }, [])

  const filterReviews = (start, end) => {
    if (!start && !end) {
      setFilteredReviews(reviews)
      return
    }
    const startDate = start ? new Date(start.setHours(0, 0, 0, 0)) : null
    const endDate = end ? new Date(end.setHours(23, 59, 59, 999)) : null

    let filtered = reviews.filter(review => {
      const reviewDate = new Date(review.date_time)
      const matchesStart = !startDate || reviewDate >= startDate
      const matchesEnd = !endDate || reviewDate <= endDate
      return matchesStart && matchesEnd
    })
    filtered = filtered.sort((a, b) => new Date(b.date_time) - new Date(a.date_time))

    setFilteredReviews(filtered)
  }

  if (loading) return <div className="panel">Загрузка отзывов...</div>

  return (
    <div className="panel">
      <div className="panel-header">
        <h2 className="panel-title">Отзывы</h2>
        <div className="date-filter">
          <div className="date-picker">
            <label>От:</label>
            <DatePicker
              selected={startDate}
              onChange={(date) => {
                setStartDate(date)
                filterReviews(date, endDate)
              }}
              selectsStart
              startDate={startDate}
              endDate={endDate}
              dateFormat="dd.MM.yyyy"
              placeholderText="Выберите дату"
            />
          </div>
          <div className="date-picker">
            <label>До:</label>
            <DatePicker
              selected={endDate}
              onChange={(date) => {
                setEndDate(date)
                filterReviews(startDate, date)
              }}
              selectsEnd
              startDate={startDate}
              endDate={endDate}
              minDate={startDate}
              dateFormat="dd.MM.yyyy"
              placeholderText="Выберите дату"
            />
          </div>
        </div>
        {window.location.pathname.includes('/users/') && (
          <button 
            onClick={() => navigate('/users')}
            className="back-button"
          >
            Назад к пользователям
          </button>
        )}
      </div>

      <table className="table">
        <thead>
          <tr>
            <th>Комментарий</th>
            <th>Пользователь</th>
            <th>Номер</th>
            <th>Роль</th>
            <th>Дата</th>
          </tr>
        </thead>
        <tbody>
          {filteredReviews.map(review => (
            <tr key={review.id}>
              <td>{review.comment}</td>
              <td>{review.user_name}</td>
              <td>{review.user_phone}</td>
              <td>{review.role_name}</td>
              <td>{new Date(review.date_time).toLocaleString()}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

export default ReviewsList
