# 🧪 Test Data for API Testing

## 📋 Quick Setup Script

Save this as `setup_test_data.sh` and run it to create comprehensive test data:

```bash
#!/bin/bash

BASE_URL="http://localhost:8001/api"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 Setting up test data for Volunteering Platform API${NC}"

# Function to make API calls
api_call() {
    local method=$1
    local endpoint=$2
    local data=$3
    local token=$4
    
    if [ -n "$token" ]; then
        curl -s -X $method "$BASE_URL$endpoint" \
            -H "Content-Type: application/json" \
            -H "Authorization: Bearer $token" \
            -d "$data"
    else
        curl -s -X $method "$BASE_URL$endpoint" \
            -H "Content-Type: application/json" \
            -d "$data"
    fi
    echo
}

# Store tokens
VOLUNTEER_TOKENS=()
ORG_TOKENS=()
ADMIN_TOKEN=""

echo -e "${YELLOW}📝 Creating 10 Volunteers...${NC}"

# Create 10 Volunteers
for i in {1..10}; do
    echo "Creating volunteer $i..."
    
    response=$(api_call "POST" "/auth/register/volunteer/" "{
        \"username\": \"volunteer$i\",
        \"email\": \"volunteer$i@test.com\",
        \"password\": \"testpass123\",
        \"password_confirm\": \"testpass123\",
        \"first_name\": \"Волонтер$i\",
        \"last_name\": \"Тестовый\",
        \"birth_date\": \"199$i-0$(($i%9+1))-15\",
        \"gender\": \"$([ $((i%2)) -eq 0 ] && echo \"male\" || echo \"female\")\",
        \"city\": \"Алматы\",
        \"region\": \"Алматы\",
        \"skills\": [\"программирование\", \"дизайн\", \"маркетинг\", \"педагогика\", \"медицина\"],
        \"interests\": [\"образование\", \"экология\", \"спорт\", \"культура\", \"здоровье\"]
    }")
    
    # Extract token
    token=$(echo $response | grep -o '"access":"[^"]*"' | cut -d'"' -f4)
    VOLUNTEER_TOKENS+=($token)
    
    if [ -n "$token" ]; then
        echo -e "${GREEN}✅ Volunteer $i created${NC}"
    else
        echo -e "${RED}❌ Failed to create volunteer $i${NC}"
    fi
done

echo -e "${YELLOW}🏢 Creating 10 Organizations...${NC}"

# Create 10 Organizations
for i in {1..10}; do
    echo "Creating organization $i..."
    
    response=$(api_call "POST" "/auth/register/organization/" "{
        \"username\": \"org$i\",
        \"email\": \"org$i@test.com\",
        \"password\": \"testpass123\",
        \"password_confirm\": \"testpass123\",
        \"organization_name\": \"Организация $i\",
        \"organization_type\": \"$([ $((i%3)) -eq 0 ] && echo \"ngo\" || ([ $((i%3)) -eq 1 ] && echo \"initiative\" || echo \"government\"))\",
        \"description\": \"Описание организации $i - мы помогаем людям и делаем мир лучше\",
        \"city\": \"Алматы\",
        \"region\": \"Алматы\",
        \"contact_phone\": \"+7 777 123 456$i\",
        \"contact_email\": \"contact@org$i.kz\",
        \"website\": \"https://org$i.kz\"
    }")
    
    # Extract token
    token=$(echo $response | grep -o '"access":"[^"]*"' | cut -d'"' -f4)
    ORG_TOKENS+=($token)
    
    if [ -n "$token" ]; then
        echo -e "${GREEN}✅ Organization $i created${NC}"
    else
        echo -e "${RED}❌ Failed to create organization $i${NC}"
    fi
done

echo -e "${YELLOW}📊 Creating Projects...${NC}"

# Create Projects (2 per organization)
for i in {0..9}; do
    org_token=${ORG_TOKENS[$i]}
    
    # Project 1
    echo "Creating project 1 for organization $((i+1))..."
    response=$(api_call "POST" "/projects/" "{
        \"title\": \"Проект $((i*2+1)): Помощь нуждающимся\",
        \"description\": \"Описание проекта $((i*2+1)) - помогаем тем, кто в нужде\",
        \"category_id\": $(((i%5)+1)),
        \"region_id\": $(((i%3)+1)),
        \"format\": \"$([ $((i%2)) -eq 0 ] && echo \"offline\" || echo \"online\")\",
        \"start_date\": \"2024-0$(($i%9+1))-01\",
        \"end_date\": \"2024-0$(($i%9+2))-28\",
        \"volunteers_needed\": $((10+i*5)),
        \"requirements\": \"Требования для проекта $((i*2+1))\",
        \"contact_info\": {
            \"phone\": \"+7 777 123 456$i\",
            \"email\": \"project$((i*2+1))@org$i.kz\"
        }
    }" "$org_token")
    
    # Project 2
    echo "Creating project 2 for organization $((i+1))..."
    response=$(api_call "POST" "/projects/" "{
        \"title\": \"Проект $((i*2+2)): Экологическая инициатива\",
        \"description\": \"Описание проекта $((i*2+2)) - заботимся о нашей планете\",
        \"category_id\": $((((i+1)%5)+1)),
        \"region_id\": $((((i+1)%3)+1)),
        \"format\": \"$([ $(((i+1)%2)) -eq 0 ] && echo \"online\" || echo \"offline\")\",
        \"start_date\": \"2024-0$(($i%9+1))-15\",
        \"end_date\": \"2024-0$(($i%9+3))-15\",
        \"volunteers_needed\": $((15+i*3)),
        \"requirements\": \"Требования для проекта $((i*2+2))\",
        \"contact_info\": {
            \"phone\": \"+7 777 987 654$i\",
            \"email\": \"project$((i*2+2))@org$i.kz\"
        }
    }" "$org_token")
done

echo -e "${YELLOW}📝 Submitting Applications...${NC}"

# Submit Applications (3 per volunteer)
for i in {0..9}; do
    volunteer_token=${VOLUNTEER_TOKENS[$i]}
    
    for j in {1..3}; do
        project_id=$((i*2 + j))
        echo "Volunteer $((i+1)) applying for project $project_id..."
        
        response=$(api_call "POST" "/applications/" "{
            \"project\": $project_id,
            \"cover_letter\": \"Хочу участвовать в проекте $project_id. У меня есть опыт и желание помогать.\",
            \"hours_committed\": $((10+j*5))
        }" "$volunteer_token")
    done
done

echo -e "${YELLOW}📊 Creating Reports...${NC}"

# Create Reports for first 5 projects
for i in {0..4}; do
    org_token=${ORG_TOKENS[$i]}
    project_id=$((i*2+1))
    
    echo "Creating report for project $project_id..."
    response=$(api_call "POST" "/reports/" "{
        \"project\": $project_id,
        \"title\": \"Отчет по проекту $project_id\",
        \"description\": \"Проект успешно завершен, все цели достигнуты\",
        \"goals_achieved\": \"Помогли $((20+i*10)) людям, достигли всех поставленных целей\",
        \"challenges_faced\": \"Основные сложности: координация волонтеров, погодные условия\",
        \"total_volunteers_participated\": $((5+i*2)),
        \"total_volunteer_hours\": $((50+i*20)),
        \"beneficiaries_count\": $((20+i*10)),
        \"lessons_learned\": \"Главный урок: командная работа решает любые задачи\",
        \"future_plans\": \"Планируем продолжить проект в следующем году с большим масштабом\"
    }" "$org_token")
done

echo -e "${GREEN}✅ Test data setup completed!${NC}"
echo -e "${YELLOW}📊 Summary:${NC}"
echo "- 10 Volunteers created"
echo "- 10 Organizations created"
echo "- 20 Projects created"
echo "- 30 Applications submitted"
echo "- 5 Reports created"
echo ""
echo -e "${YELLOW}🔑 Tokens saved for testing:${NC}"
echo "Volunteer tokens: ${#VOLUNTEER_TOKENS[@]}"
echo "Organization tokens: ${#ORG_TOKENS[@]}"
echo ""
echo -e "${GREEN}🚀 Ready for API testing!${NC}"
```

## 🧪 Individual Test Commands

### Volunteer Registration Test
```bash
# Test volunteer 1
curl -X POST http://localhost:8001/api/auth/register/volunteer/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "test_volunteer",
    "email": "test_volunteer@test.com",
    "password": "testpass123",
    "password_confirm": "testpass123",
    "first_name": "Александр",
    "last_name": "Тестов",
    "birth_date": "1990-05-15",
    "gender": "male",
    "city": "Алматы",
    "region": "Алматы",
    "skills": ["программирование", "английский язык"],
    "interests": ["образование", "технологии"]
  }'
```

### Organization Registration Test
```bash
# Test organization 1
curl -X POST http://localhost:8001/api/auth/register/organization/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "test_org",
    "email": "test_org@test.com",
    "password": "testpass123",
    "password_confirm": "testpass123",
    "organization_name": "Тестовая Организация",
    "organization_type": "ngo",
    "description": "Мы тестируем API и помогаем людям",
    "city": "Алматы",
    "region": "Алматы",
    "contact_phone": "+7 777 123 4567",
    "contact_email": "contact@test-org.kz",
    "website": "https://test-org.kz"
  }'
```

### Project Creation Test
```bash
# Login as organization first
ORG_TOKEN=$(curl -s -X POST http://localhost:8001/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test_org@test.com",
    "password": "testpass123"
  }' | grep -o '"access":"[^"]*"' | cut -d'"' -f4)

# Create project
curl -X POST http://localhost:8001/api/projects/ \
  -H "Authorization: Bearer $ORG_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Тестовый проект: Обучение детей",
    "description": "Обучаем детей программированию и английскому языку",
    "category_id": 1,
    "region_id": 1,
    "format": "offline",
    "start_date": "2024-03-01",
    "end_date": "2024-05-31",
    "volunteers_needed": 10,
    "requirements": "Знание английского языка, опыт с детьми",
    "contact_info": {
      "phone": "+7 777 123 4567",
      "email": "education@test-org.kz"
    }
  }'
```

### Application Test
```bash
# Login as volunteer first
VOL_TOKEN=$(curl -s -X POST http://localhost:8001/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test_volunteer@test.com",
    "password": "testpass123"
  }' | grep -o '"access":"[^"]*"' | cut -d'"' -f4)

# Submit application
curl -X POST http://localhost:8001/api/applications/ \
  -H "Authorization: Bearer $VOL_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "project": 1,
    "cover_letter": "Хочу помочь детям изучать программирование. У меня есть опыт преподавания и я люблю работать с детьми.",
    "hours_committed": 20
  }'
```

### Report Creation Test
```bash
# Create report (organization only)
curl -X POST http://localhost:8001/api/reports/ \
  -H "Authorization: Bearer $ORG_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "project": 1,
    "title": "Отчет по проекту обучения детей",
    "description": "Проект успешно завершен, дети научились основам программирования",
    "goals_achieved": "15 детей прошли курс, 10 создали свои первые проекты",
    "challenges_faced": "Сложности с онлайн-обучением, технические проблемы",
    "total_volunteers_participated": 5,
    "total_volunteer_hours": 100,
    "beneficiaries_count": 15,
    "lessons_learned": "Онлайн-формат требует хорошей подготовки технической базы",
    "future_plans": "Планируем продолжить проект с улучшенной технической базой"
  }'
```

## 📊 Test Data Summary

### Users Created:
- **10 Volunteers** with diverse skills and interests
- **10 Organizations** (NGO, Initiative, Government)
- **1 Admin** (manual setup required)

### Projects Created:
- **20 Projects** (2 per organization)
- Different categories and regions
- Mix of online/offline formats
- Various volunteer requirements

### Applications Submitted:
- **30 Applications** (3 per volunteer)
- Distributed across different projects
- Various hour commitments

### Reports Created:
- **5 Reports** (for first 5 projects)
- Complete project statistics
- Detailed achievements and challenges

## 🔍 Testing Scenarios

### 1. **Happy Path Testing**
- Register users → Create projects → Submit applications → Approve → Create reports

### 2. **Permission Testing**
- Volunteer trying to create project (should fail)
- Organization trying to approve other org's project (should fail)
- Admin operations (should succeed)

### 3. **Rate Limiting Testing**
- Multiple login attempts quickly
- Rapid project creation
- Bulk application submissions

### 4. **Error Handling Testing**
- Invalid data submission
- Missing required fields
- Unauthorized access attempts

## 🚀 Quick Test Run

```bash
# Make script executable
chmod +x setup_test_data.sh

# Run the script
./setup_test_data.sh

# Test specific endpoints using saved tokens
VOL_TOKEN=${VOLUNTEER_TOKENS[0]}
ORG_TOKEN=${ORG_TOKENS[0]}

curl -H "Authorization: Bearer $VOL_TOKEN" http://localhost:8001/api/applications/
curl -H "Authorization: Bearer $ORG_TOKEN" http://localhost:8001/api/projects/
```

**Happy testing! 🧪✨**
